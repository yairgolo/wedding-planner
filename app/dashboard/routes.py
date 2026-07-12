from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models import Guest, SeatingAssignment, SeatingTable, Wedding

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    active_guests = []
    if wedding:
        active_guests = db.session.scalars(
            db.select(Guest).where(Guest.wedding_id == wedding.id, Guest.deleted_at.is_(None))
        ).all()
    metrics = {
        "guests": sum(guest.invited_count for guest in active_guests),
        "confirmed": sum(
            guest.confirmed_count for guest in active_guests if guest.rsvp_status == "confirmed"
        ),
        "pending": sum(
            guest.invited_count
            for guest in active_guests
            if guest.rsvp_status in {"pending", "maybe"}
        ),
        "declined": sum(
            guest.invited_count for guest in active_guests if guest.rsvp_status == "declined"
        ),
        "tasks": 0,
        "unseated": 0,
        "purchases": 0,
    }
    if wedding:
        assigned_guest_ids = set(
            db.session.scalars(
                db.select(SeatingAssignment.guest_id).where(
                    SeatingAssignment.wedding_id == wedding.id
                )
            ).all()
        )
        metrics["unseated"] = sum(
            (guest.confirmed_count if guest.rsvp_status == "confirmed" else guest.invited_count)
            for guest in active_guests
            if guest.rsvp_status != "declined" and guest.id not in assigned_guest_ids
        )
        metrics["tables"] = db.session.scalar(
            db.select(db.func.count(SeatingTable.id)).where(SeatingTable.wedding_id == wedding.id)
        ) or 0
    return render_template("dashboard/index.html", wedding=wedding, metrics=metrics)


@dashboard_bp.get("/health")
def health():
    return {"status": "ok"}, 200
