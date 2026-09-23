from __future__ import annotations

import secrets
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from PIL import Image, UnidentifiedImageError
from sqlalchemy import or_, update
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash

from app.extensions import db, limiter
from app.models import (
    InvitationPortalActivity,
    InvitationPortalGuest,
    InvitationPortalSettings,
    InvitationSendAttempt,
    InvitationSender,
    User,
)

from .forms import ImageForm, MessageForm, PortalGuestForm, PortalLoginForm, SenderForm

invite_portal_bp = Blueprint("invite_portal", __name__, url_prefix="/invite-manager")
DEFAULT_TEMPLATES = {
    "male": (
        "{name} היקר,\n\nבהתרגשות גדולה, נשמח להזמינך לחגוג איתנו את יום חתונתנו."
        "\nהנוכחות שלך תהפוך את השמחה לשלמה.\n\nמחכים לחגוג יחד 🤍"
    ),
    "female": (
        "{name} היקרה,\n\nבהתרגשות גדולה, נשמח להזמינך לחגוג איתנו את יום חתונתנו."
        "\nהנוכחות שלך תהפוך את השמחה לשלמה.\n\nמחכים לחגוג יחד 🤍"
    ),
    "plural": (
        "{name} היקרים,\n\nבהתרגשות גדולה, נשמח להזמינכם לחגוג איתנו את יום חתונתנו."
        "\nהנוכחות שלכם תהפוך את השמחה לשלמה.\n\nמחכים לחגוג יחד 🤍"
    ),
}
SIDE_LABELS = {"groom": "חתן", "bride": "כלה"}
SALUTATION_LABELS = {"male": "זכר", "female": "נקבה", "plural": "רבים"}
STATUS_LABELS = {"unsent": "טרם נשלח", "preparing": "בטיפול", "sent": "נשלח"}
DECISION_LABELS = {"invited": "כן, מזמינים", "undecided": "בסימן שאלה"}


def now():
    return datetime.now(timezone.utc)


def clean_phone(value):
    cleaned = "".join(ch for ch in str(value or "") if ch.isdigit() or ch == "+")
    # Excel sometimes removes the leading zero in an Israeli mobile number.
    if len(cleaned) == 9 and cleaned.startswith("5"):
        cleaned = "0" + cleaned
    return cleaned or None


def whatsapp_phone(value):
    phone = clean_phone(value) or ""
    if phone.startswith("00"):
        phone = phone[2:]
    if phone.startswith("0"):
        phone = "972" + phone[1:]
    phone = phone.lstrip("+")
    return phone if phone.isascii() and phone.isdigit() and 8 <= len(phone) <= 15 else None


def settings():
    item = db.session.get(InvitationPortalSettings, 1)
    if item is None:
        item = InvitationPortalSettings(id=1)
        db.session.add(item)
        db.session.commit()
    return item


def admin_user():
    user_id = session.get("invite_portal_admin_id")
    user = db.session.get(User, user_id) if user_id else None
    return user if user and user.is_admin and user.is_active else None


def require_admin():
    user = admin_user()
    if not user:
        abort(401, description="יש להתחבר מחדש כדי להמשיך.")
    return user


def sender_for_token(token):
    sender = db.session.scalar(
        db.select(InvitationSender).where(InvitationSender.access_token == token)
    )
    if not sender or not sender.is_active:
        abort(404, description="הקישור אינו פעיל. בקשו מהמנהל קישור חדש.")
    return sender


def guest_or_404(guest_id, sender=None, include_deleted=False):
    guest = db.get_or_404(InvitationPortalGuest, guest_id)
    if sender and guest.side != sender.side:
        abort(404)
    if guest.deleted_at and not include_deleted:
        abort(404, description="המוזמן נמחק. ניתן לשחזר אותו מרשימת המחוקים.")
    return guest


def readable_message(sender, guest):
    template = (
        getattr(sender, f"{guest.salutation}_template")
        if sender
        else DEFAULT_TEMPLATES[guest.salutation]
    )
    return template.replace("{name}", guest.first_name).strip()


def activity(guest, sender, action):
    db.session.add(
        InvitationPortalActivity(
            guest_id=guest.id, sender_id=sender.id if sender else None, action=action
        )
    )


@invite_portal_bp.errorhandler(HTTPException)
def portal_error(error):
    if request.accept_mimetypes.best == "application/json":
        return jsonify(ok=False, error=error.description), error.code
    if error.code == 401:
        return redirect(url_for("invite_portal.admin_login"))
    return render_template(
        "invite_portal/error.html",
        admin=False,
        sender=None,
        code=error.code,
        message=error.description,
    ), error.code


@invite_portal_bp.after_request
def private_response(response):
    response.headers["Cache-Control"] = "no-store"
    # HTTPS CSRF validation needs a same-origin Referer. Never expose token URLs externally.
    response.headers["Referrer-Policy"] = "same-origin"
    return response


@invite_portal_bp.context_processor
def portal_context():
    return dict(
        side_labels=SIDE_LABELS,
        salutation_labels=SALUTATION_LABELS,
        status_labels=STATUS_LABELS,
        decision_labels=DECISION_LABELS,
    )


@invite_portal_bp.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def admin_login():
    if admin_user():
        return redirect(url_for("invite_portal.admin_index"))
    form = PortalLoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(User.email == form.email.data.strip().lower())
        )
        if (
            user
            and user.is_admin
            and user.is_active
            and check_password_hash(user.password_hash, form.password.data)
        ):
            session["invite_portal_admin_id"] = user.id
            session.permanent = True
            return redirect(url_for("invite_portal.admin_index"))
        form.password.errors.append("פרטי הכניסה אינם נכונים.")
    return render_template("invite_portal/login.html", form=form, admin=False, sender=None)


@invite_portal_bp.post("/admin/logout")
def admin_logout():
    session.pop("invite_portal_admin_id", None)
    return redirect(url_for("invite_portal.admin_login"))


@invite_portal_bp.get("/")
def home():
    return redirect(url_for("invite_portal.admin_index"))


def dashboard(sender=None):
    scope = db.select(InvitationPortalGuest).where(InvitationPortalGuest.deleted_at.is_(None))
    if sender:
        scope = scope.where(InvitationPortalGuest.side == sender.side)
    all_guests = db.session.scalars(scope).all()
    query = request.args.get("q", "").strip()
    if query:
        like = f"%{query}%"
        scope = scope.where(
            or_(
                InvitationPortalGuest.first_name.ilike(like),
                InvitationPortalGuest.last_name.ilike(like),
                InvitationPortalGuest.phone.ilike(like),
            )
        )
    for field, allowed in (
        ("status", STATUS_LABELS),
        ("side", SIDE_LABELS),
        ("invitation_decision", DECISION_LABELS),
    ):
        value = request.args.get(field, "")
        if value in allowed:
            scope = scope.where(getattr(InvitationPortalGuest, field) == value)
    group = request.args.get("group", "")
    if group:
        scope = scope.where(InvitationPortalGuest.group_name == group)
    return render_template(
        "invite_portal/dashboard.html",
        admin=sender is None,
        sender=sender,
        guests=db.session.scalars(scope.order_by(InvitationPortalGuest.first_name)).all(),
        stats={key: sum(g.status == key for g in all_guests) for key in STATUS_LABELS},
        undecided_count=sum(g.invitation_decision == "undecided" for g in all_guests),
        groups=sorted({g.group_name for g in all_guests if g.group_name}),
        settings=settings(),
        senders=db.session.scalars(
            db.select(InvitationSender)
            .where(InvitationSender.is_active.is_(True))
            .order_by(InvitationSender.name)
        ).all()
        if sender is None
        else [],
    )


@invite_portal_bp.get("/admin")
def admin_index():
    require_admin()
    return dashboard()


@invite_portal_bp.get("/u/<token>")
def user_index(token):
    return dashboard(sender_for_token(token))


def save_guest_form(guest_id=None, sender=None):
    guest = (
        guest_or_404(guest_id, sender)
        if guest_id
        else InvitationPortalGuest(
            side=sender.side if sender else "groom", salutation="", invitation_decision="invited"
        )
    )
    form = PortalGuestForm(obj=guest)
    if sender:
        form.side.data = sender.side
    if form.validate_on_submit():
        # A manual edit supersedes an in-progress invitation.
        invalidate_attempts(guest.id)
        if guest.status == "preparing":
            guest.status = "sent" if guest.sent_at else "unsent"
        form.populate_obj(guest)
        guest.phone = clean_phone(form.phone.data)
        db.session.add(guest)
        db.session.commit()
        flash("המוזמן נשמר.", "success")
        return redirect(index_url(sender))
    return render_template(
        "invite_portal/guest_form.html",
        form=form,
        guest=guest,
        admin=sender is None,
        sender=sender,
    )


def index_url(sender=None):
    return (
        url_for("invite_portal.user_index", token=sender.access_token)
        if sender
        else url_for("invite_portal.admin_index")
    )


@invite_portal_bp.route("/admin/guest/new", methods=["GET", "POST"])
@invite_portal_bp.route("/admin/guest/<int:guest_id>/edit", methods=["GET", "POST"])
def admin_guest_form(guest_id=None):
    require_admin()
    return save_guest_form(guest_id)


@invite_portal_bp.route("/u/<token>/guest/new", methods=["GET", "POST"])
@invite_portal_bp.route("/u/<token>/guest/<int:guest_id>/edit", methods=["GET", "POST"])
def user_guest_form(token, guest_id=None):
    return save_guest_form(guest_id, sender_for_token(token))


def invalidate_attempts(guest_id):
    if guest_id:
        db.session.execute(
            update(InvitationSendAttempt)
            .where(
                InvitationSendAttempt.guest_id == guest_id,
                InvitationSendAttempt.state == "pending",
            )
            .values(state="cancelled")
        )


def require_invited(guest):
    if guest.invitation_decision != "invited":
        abort(409, description="המוזמן בסימן שאלה. יש לשנות ל׳כן, מזמינים׳ לפני השליחה.")


def close_pending(guest):
    if guest.status == "preparing":
        pending = db.session.scalar(
            db.select(InvitationSendAttempt).where(
                InvitationSendAttempt.guest_id == guest.id,
                InvitationSendAttempt.state == "pending",
            )
        )
        guest.status = pending.prior_status if pending else ("sent" if guest.sent_at else "unsent")
    invalidate_attempts(guest.id)


def change_decision(guest, sender=None):
    decision = request.form.get("invitation_decision")
    if decision not in DECISION_LABELS:
        abort(400, description="יש לבחור כן, מזמינים או בסימן שאלה.")
    close_pending(guest)
    guest.invitation_decision = decision
    activity(guest, sender, f"decision_{decision}")
    db.session.commit()
    flash(f"{guest.full_name}: {DECISION_LABELS[decision]}.", "success")
    return redirect(index_url(sender))


@invite_portal_bp.post("/admin/guest/<int:guest_id>/decision")
def admin_guest_decision(guest_id):
    require_admin()
    return change_decision(guest_or_404(guest_id))


@invite_portal_bp.post("/u/<token>/guest/<int:guest_id>/decision")
def user_guest_decision(token, guest_id):
    sender = sender_for_token(token)
    return change_decision(guest_or_404(guest_id, sender), sender)


def delete_guest(guest, sender=None):
    close_pending(guest)
    guest.deleted_at = now()
    activity(guest, sender, "deleted")
    db.session.commit()
    flash(f"{guest.full_name} הוסר מהרשימה. אפשר לשחזר דרך ׳מוזמנים שנמחקו׳.", "success")
    return redirect(index_url(sender))


@invite_portal_bp.post("/admin/guest/<int:guest_id>/delete")
def admin_delete_guest(guest_id):
    require_admin()
    return delete_guest(guest_or_404(guest_id))


@invite_portal_bp.post("/u/<token>/guest/<int:guest_id>/delete")
def user_delete_guest(token, guest_id):
    sender = sender_for_token(token)
    return delete_guest(guest_or_404(guest_id, sender), sender)


def trash_page(sender=None):
    query = db.select(InvitationPortalGuest).where(InvitationPortalGuest.deleted_at.is_not(None))
    if sender:
        query = query.where(InvitationPortalGuest.side == sender.side)
    return render_template(
        "invite_portal/trash.html",
        sender=sender,
        admin=sender is None,
        guests=db.session.scalars(query.order_by(InvitationPortalGuest.deleted_at.desc())).all(),
    )


@invite_portal_bp.get("/admin/trash")
def admin_trash():
    require_admin()
    return trash_page()


@invite_portal_bp.get("/u/<token>/trash")
def user_trash(token):
    return trash_page(sender_for_token(token))


def restore_guest(guest, sender=None):
    guest.deleted_at = None
    activity(guest, sender, "restored")
    db.session.commit()
    flash(f"{guest.full_name} שוחזר לרשימה.", "success")
    return redirect(index_url(sender))


@invite_portal_bp.post("/admin/guest/<int:guest_id>/restore")
def admin_restore_guest(guest_id):
    require_admin()
    return restore_guest(guest_or_404(guest_id, include_deleted=True))


@invite_portal_bp.post("/u/<token>/guest/<int:guest_id>/restore")
def user_restore_guest(token, guest_id):
    sender = sender_for_token(token)
    return restore_guest(guest_or_404(guest_id, sender, include_deleted=True), sender)


def change_status(guest, sender=None):
    status = request.form.get("status")
    if status not in STATUS_LABELS:
        abort(400, description="סטטוס לא תקין.")
    if status in {"preparing", "sent"}:
        require_invited(guest)
    invalidate_attempts(guest.id)
    guest.status = status
    guest.sent_at = now() if status == "sent" else None
    guest.last_sender_id = sender.id if sender and status == "sent" else None
    activity(guest, sender, f"status_{status}")
    db.session.commit()
    flash("הסטטוס עודכן.", "success")
    return redirect(index_url(sender))


@invite_portal_bp.post("/admin/guest/<int:guest_id>/status")
def admin_guest_status(guest_id):
    require_admin()
    return change_status(guest_or_404(guest_id))


@invite_portal_bp.post("/u/<token>/guest/<int:guest_id>/status")
def user_guest_status(token, guest_id):
    sender = sender_for_token(token)
    return change_status(guest_or_404(guest_id, sender), sender)


@invite_portal_bp.route("/admin/senders", methods=["GET", "POST"])
@invite_portal_bp.route("/admin/senders/<int:sender_id>", methods=["GET", "POST"])
def admin_senders(sender_id=None):
    require_admin()
    sender = (
        db.get_or_404(InvitationSender, sender_id)
        if sender_id
        else InvitationSender(
            side="groom",
            is_active=True,
            **{f"{key}_template": value for key, value in DEFAULT_TEMPLATES.items()},
        )
    )
    form = SenderForm(obj=sender)
    if form.validate_on_submit():
        form.populate_obj(sender)
        db.session.add(sender)
        db.session.commit()
        flash("פרופיל השולח נשמר.", "success")
        return redirect(url_for("invite_portal.admin_senders"))
    return render_template(
        "invite_portal/senders.html",
        form=form,
        editing=sender_id is not None,
        sender=None,
        editing_sender=sender,
        admin=True,
        senders=db.session.scalars(
            db.select(InvitationSender).order_by(InvitationSender.side, InvitationSender.name)
        ).all(),
    )


@invite_portal_bp.route("/u/<token>/message", methods=["GET", "POST"])
def user_message(token):
    sender = sender_for_token(token)
    form = MessageForm(obj=sender)
    if form.validate_on_submit():
        form.populate_obj(sender)
        db.session.commit()
        flash("הנוסחים האישיים נשמרו.", "success")
        return redirect(index_url(sender))
    return render_template("invite_portal/message.html", form=form, sender=sender, admin=False)


@invite_portal_bp.post("/admin/senders/<int:sender_id>/renew")
def renew_sender_link(sender_id):
    require_admin()
    sender = db.get_or_404(InvitationSender, sender_id)
    sender.access_token = secrets.token_urlsafe(32)
    db.session.commit()
    flash("נוצר קישור חדש. הקישור הקודם בוטל.", "success")
    return redirect(url_for("invite_portal.admin_senders"))


@invite_portal_bp.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    require_admin()
    item = settings()
    form = ImageForm()
    if form.validate_on_submit():
        if not form.image.data:
            form.image.errors.append("יש לבחור תמונה להעלאה.")
        else:
            try:
                image = Image.open(form.image.data.stream)
                image.verify()
                form.image.data.stream.seek(0)
                image = Image.open(form.image.data.stream).convert("RGB")
                image.thumbnail((2400, 3200))
                filename = f"invite-portal-{secrets.token_hex(8)}.jpg"
                image.save(
                    Path(current_app.config["UPLOAD_FOLDER"]) / filename,
                    "JPEG",
                    quality=92,
                    optimize=True,
                )
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                form.image.errors.append("הקובץ אינו תמונה תקינה או שהוא גדול מדי.")
            else:
                # Keep earlier uploads so a share already being prepared remains usable.
                item.image_filename = filename
                db.session.commit()
                flash("תמונת ההזמנה עודכנה.", "success")
                return redirect(url_for("invite_portal.admin_settings"))
    return render_template(
        "invite_portal/settings.html", admin=True, sender=None, form=form, settings=item
    )


@invite_portal_bp.get("/image")
def image():
    item = settings()
    if not item.image_filename:
        abort(404, description="עדיין לא הועלתה תמונת הזמנה.")
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], item.image_filename)


def send_actor(token=None):
    if token is not None:
        sender = sender_for_token(token)
        return sender, None
    return None, require_admin().id


def prepare(guest_id, token=None):
    actor_sender, actor_admin = send_actor(token)
    guest = guest_or_404(guest_id, actor_sender)
    require_invited(guest)
    item = settings()
    if (
        not item.image_filename
        or not (Path(current_app.config["UPLOAD_FOLDER"]) / item.image_filename).is_file()
    ):
        abort(400, description="יש להעלות תמונת הזמנה בעמוד ההגדרות לפני השליחה.")
    sender = actor_sender
    if actor_admin and request.form.get("sender_id"):
        sender = db.session.get(InvitationSender, request.form.get("sender_id", type=int))
        if not sender or not sender.is_active or sender.side != guest.side:
            abort(400, description="בחרו שולח פעיל מהצד של המוזמן.")
    pending = db.session.scalar(
        db.select(InvitationSendAttempt).where(
            InvitationSendAttempt.guest_id == guest.id, InvitationSendAttempt.state == "pending"
        )
    )
    if pending:
        if pending.admin_user_id != actor_admin or (
            actor_admin is None and pending.sender_id != actor_sender.id
        ):
            abort(409, description="המוזמן כבר בטיפול אצל שולח אחר. רעננו או עדכנו את הסטטוס.")
        attempt = pending
    else:
        # Compare-and-swap prevents two requests from starting different sends concurrently.
        result = db.session.execute(
            update(InvitationPortalGuest)
            .where(
                InvitationPortalGuest.id == guest.id,
                InvitationPortalGuest.updated_at == guest.updated_at,
                InvitationPortalGuest.deleted_at.is_(None),
                InvitationPortalGuest.invitation_decision == "invited",
            )
            .values(status="preparing", updated_at=now()),
            execution_options={"synchronize_session": False},
        )
        if result.rowcount != 1:
            db.session.rollback()
            abort(409, description="הרשומה השתנתה. רעננו ונסו שוב.")
        attempt = InvitationSendAttempt(
            guest_id=guest.id,
            sender_id=sender.id if sender else None,
            admin_user_id=actor_admin,
            prior_status=(
                guest.status
                if guest.status != "preparing"
                else ("sent" if guest.sent_at else "unsent")
            ),
            message=readable_message(sender, guest),
        )
        db.session.add(attempt)
        activity(guest, sender, "preparing")
        db.session.commit()
    return jsonify(
        ok=True,
        attempt=attempt.id,
        text=attempt.message,
        name=guest.full_name,
        phone=guest.phone,
        whatsapp_phone=whatsapp_phone(guest.phone),
        image_url=url_for("invite_portal.image"),
        resumed=pending is not None,
        sender_name=attempt.sender.name if attempt.sender else "מנהל",
    )


def confirm(guest_id, token=None):
    actor_sender, actor_admin = send_actor(token)
    guest = guest_or_404(guest_id, actor_sender)
    decision = request.form.get("sent")
    if decision not in {"true", "false"}:
        abort(400, description="יש לבחור נשלח או ביטול.")
    if decision == "true":
        require_invited(guest)
    attempt = db.session.get(InvitationSendAttempt, request.form.get("attempt", ""))
    if not attempt or attempt.guest_id != guest.id:
        abort(400, description="לא נמצא ניסיון שליחה. פתחו מחדש את ההזמנה.")
    if attempt.admin_user_id != actor_admin or (
        actor_admin is None and attempt.sender_id != actor_sender.id
    ):
        abort(403, description="רק מי שהתחיל את השליחה יכול לאשר אותה.")
    target = "confirmed" if decision == "true" else "cancelled"
    if attempt.state == target:
        return jsonify(ok=True)  # Retrying the same confirmation never counts twice.
    result = db.session.execute(
        update(InvitationSendAttempt)
        .where(
            InvitationSendAttempt.id == attempt.id,
            InvitationSendAttempt.state == "pending",
        )
        .values(state=target)
    )
    if result.rowcount != 1:
        db.session.rollback()
        abort(409, description="ניסיון השליחה כבר נסגר. רעננו את הרשימה.")
    if decision == "true":
        guest.status = "sent"
        guest.sent_at = now()
        guest.last_sender_id = attempt.sender_id
        guest.attempts += 1
    else:
        guest.status = attempt.prior_status
    activity(guest, attempt.sender, "sent" if decision == "true" else "cancelled")
    db.session.commit()
    return jsonify(ok=True)


@invite_portal_bp.post("/admin/guest/<int:guest_id>/prepare")
@limiter.limit("120 per hour")
def admin_prepare_send(guest_id):
    return prepare(guest_id)


@invite_portal_bp.post("/admin/guest/<int:guest_id>/confirm")
def admin_confirm_send(guest_id):
    return confirm(guest_id)


@invite_portal_bp.post("/u/<token>/guest/<int:guest_id>/prepare")
@limiter.limit("120 per hour")
def prepare_send(token, guest_id):
    return prepare(guest_id, token)


@invite_portal_bp.post("/u/<token>/guest/<int:guest_id>/confirm")
def confirm_send(token, guest_id):
    return confirm(guest_id, token)


# Register Excel handlers after the shared authorization helpers are defined.
from . import excel  # noqa: E402,F401
