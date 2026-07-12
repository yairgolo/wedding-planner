from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models import Guest, Task, Vendor, Wedding

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


def build_notifications(wedding):
    guests = db.session.scalars(
        db.select(Guest).where(Guest.wedding_id == wedding.id, Guest.deleted_at.is_(None))
    ).all()
    tasks = db.session.scalars(
        db.select(Task).where(Task.wedding_id == wedding.id, Task.deleted_at.is_(None))
    ).all()
    vendors = db.session.scalars(
        db.select(Vendor).where(Vendor.wedding_id == wedding.id, Vendor.deleted_at.is_(None))
    ).all()
    items = []
    pending = sum(g.invited_count for g in guests if g.rsvp_status in {"pending", "maybe"})
    unsent = sum(g.invited_count for g in guests if not g.invitation_sent)
    overdue_tasks = [t for t in tasks if t.is_overdue]
    overdue_vendors = [v for v in vendors if v.is_payment_overdue]
    unsigned = [v for v in vendors if v.status in {"booked", "completed"} and not v.contract_signed]
    if unsent:
        items.append(
            ("💌", f"{unsent} מוזמנים עדיין לא קיבלו הזמנה", "invitations.index", "warning")
        )
    if pending:
        items.append(("⏳", f"{pending} מוזמנים עדיין לא אישרו הגעה", "guests.index", "info"))
    if overdue_tasks:
        items.append(("📋", f"{len(overdue_tasks)} משימות באיחור", "tasks.index", "danger"))
    if overdue_vendors:
        items.append(
            ("💰", f"{len(overdue_vendors)} תשלומי ספקים באיחור", "vendors.index", "danger")
        )
    if unsigned:
        items.append(
            ("✍️", f"{len(unsigned)} ספקים סגורים ללא חוזה חתום", "vendors.index", "warning")
        )
    return items


@notifications_bp.get("")
@login_required
def index():
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    items = build_notifications(wedding) if wedding else []
    return render_template("notifications/index.html", items=items)
