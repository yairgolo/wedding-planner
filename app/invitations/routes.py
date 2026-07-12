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
    url_for,
)
from flask_login import current_user, login_required
from PIL import Image, UnidentifiedImageError
from sqlalchemy import or_

from app.extensions import db, limiter
from app.models import AuditLog, Guest, InvitationActivity, InvitationSettings, Wedding

from .forms import InvitationSettingsForm

invitations_bp = Blueprint("invitations", __name__, url_prefix="/invitations")

DEFAULT_MESSAGE = """שלום {name} 😊

בשמחה ובהתרגשות אנחנו מזמינים אותך לחתונה שלנו!

{couple}
{date}
{venue}
{address}

לאישור הגעה:
{rsvp_url}

נשמח לראותך איתנו ביום שמחתנו 🤍"""


def current_wedding() -> Wedding:
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    if not wedding:
        abort(404)
    return wedding


def get_settings(wedding: Wedding) -> InvitationSettings:
    settings = db.session.scalar(
        db.select(InvitationSettings).where(InvitationSettings.wedding_id == wedding.id)
    )
    if settings is None:
        settings = InvitationSettings(wedding_id=wedding.id, message_template=DEFAULT_MESSAGE)
        db.session.add(settings)
        db.session.commit()
    return settings


def format_message(settings: InvitationSettings, wedding: Wedding, guest: Guest) -> str:
    event_date = wedding.event_date.strftime("%d/%m/%Y") if wedding.event_date else ""
    values = {
        "name": guest.full_name,
        "couple": wedding.display_name,
        "date": event_date,
        "venue": wedding.venue_name or "",
        "address": wedding.venue_address or "",
        "rsvp_url": url_for("rsvp.respond", token=guest.rsvp_token, _external=True),
    }
    try:
        return settings.message_template.format_map(values).strip()
    except (KeyError, ValueError):
        return settings.message_template.strip() + "\n\n" + values["rsvp_url"]


@invitations_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    wedding = current_wedding()
    settings = get_settings(wedding)
    form = InvitationSettingsForm(obj=settings)
    if form.validate_on_submit():
        settings.message_template = form.message_template.data.strip()
        uploaded = form.image.data
        if uploaded:
            try:
                image = Image.open(uploaded.stream)
                image.verify()
                uploaded.stream.seek(0)
                image = Image.open(uploaded.stream).convert("RGB")
            except (UnidentifiedImageError, OSError):
                form.image.errors.append("הקובץ אינו תמונה תקינה.")
            else:
                filename = f"invitation-{wedding.id}-{secrets.token_hex(8)}.jpg"
                destination = Path(current_app.config["UPLOAD_FOLDER"]) / filename
                image.thumbnail((2400, 3200))
                image.save(destination, "JPEG", quality=92, optimize=True)
                if settings.image_filename:
                    old = Path(current_app.config["UPLOAD_FOLDER"]) / settings.image_filename
                    old.unlink(missing_ok=True)
                settings.image_filename = filename
        if not form.image.errors:
            db.session.add(
                AuditLog(
                    wedding_id=wedding.id,
                    user_id=current_user.id,
                    entity_type="invitation_settings",
                    entity_id=str(settings.id),
                    action="update",
                    description="עודכנו תמונת וטקסט ההזמנה",
                )
            )
            db.session.commit()
            flash("הגדרות ההזמנה נשמרו.", "success")
            return redirect(url_for("invitations.index"))

    q = request.args.get("q", "").strip()
    state = request.args.get("state", "").strip()
    stmt = db.select(Guest).where(Guest.wedding_id == wedding.id, Guest.deleted_at.is_(None))
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(
                Guest.first_name.ilike(pattern),
                Guest.last_name.ilike(pattern),
                Guest.phone.ilike(pattern),
            )
        )
    if state == "unsent":
        stmt = stmt.where(Guest.invitation_sent.is_(False))
    elif state == "sent":
        stmt = stmt.where(Guest.invitation_sent.is_(True))
    elif state == "pending":
        stmt = stmt.where(Guest.rsvp_status.in_(["pending", "maybe"]))
    guests = db.session.scalars(stmt.order_by(Guest.invitation_sent, Guest.first_name)).all()
    all_guests = db.session.scalars(
        db.select(Guest).where(Guest.wedding_id == wedding.id, Guest.deleted_at.is_(None))
    ).all()
    stats = {
        "total": len(all_guests),
        "sent": sum(1 for guest in all_guests if guest.invitation_sent),
        "unsent": sum(1 for guest in all_guests if not guest.invitation_sent),
        "pending": sum(1 for guest in all_guests if guest.rsvp_status in {"pending", "maybe"}),
    }
    return render_template(
        "invitations/index.html",
        wedding=wedding,
        settings=settings,
        form=form,
        guests=guests,
        stats=stats,
    )


@invitations_bp.get("/image")
def invitation_image():
    wedding = current_wedding()
    settings = get_settings(wedding)
    if not settings.image_filename:
        abort(404)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], settings.image_filename)


@invitations_bp.get("/guest/<int:guest_id>/share-data")
@login_required
def share_data(guest_id: int):
    wedding = current_wedding()
    settings = get_settings(wedding)
    guest = db.get_or_404(Guest, guest_id)
    if guest.wedding_id != wedding.id or guest.is_deleted:
        abort(404)
    return jsonify(
        {
            "name": guest.full_name,
            "text": format_message(settings, wedding, guest),
            "image_url": url_for("invitations.invitation_image")
            if settings.image_filename
            else None,
        }
    )


@invitations_bp.post("/guest/<int:guest_id>/shared")
@login_required
@limiter.limit("120 per hour")
def mark_shared(guest_id: int):
    wedding = current_wedding()
    guest = db.get_or_404(Guest, guest_id)
    if guest.wedding_id != wedding.id or guest.is_deleted:
        abort(404)
    activity_type = request.form.get("type", "sent")
    if activity_type not in {"sent", "reminder"}:
        abort(400)
    guest.invitation_sent = True
    guest.invitation_sent_at = datetime.now(timezone.utc)
    guest.invitation_attempts += 1
    db.session.add(
        InvitationActivity(
            wedding_id=wedding.id,
            guest_id=guest.id,
            activity_type=activity_type,
        )
    )
    db.session.commit()
    return jsonify({"ok": True, "attempts": guest.invitation_attempts})
