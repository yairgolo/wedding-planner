from decimal import Decimal

from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models import BudgetItem, Guest, ShoppingItem, Wedding

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    guests = []
    shopping = []
    budget = []
    if wedding:
        guests = db.session.scalars(
            db.select(Guest).where(Guest.wedding_id == wedding.id, Guest.deleted_at.is_(None))
        ).all()
        shopping = db.session.scalars(
            db.select(ShoppingItem).where(
                ShoppingItem.wedding_id == wedding.id, ShoppingItem.deleted_at.is_(None)
            )
        ).all()
        budget = db.session.scalars(
            db.select(BudgetItem).where(
                BudgetItem.wedding_id == wedding.id, BudgetItem.deleted_at.is_(None)
            )
        ).all()
    metrics = {
        "guests": sum(g.invited_count for g in guests),
        "confirmed": sum(g.confirmed_count for g in guests if g.rsvp_status == "confirmed"),
        "pending": sum(g.invited_count for g in guests if g.rsvp_status in {"pending", "maybe"}),
        "declined": sum(g.invited_count for g in guests if g.rsvp_status == "declined"),
        "tasks": 0,
        "unseated": sum(
            (
                g.confirmed_count
                if g.rsvp_status == "confirmed" and g.confirmed_count
                else g.invited_count
            )
            for g in guests
            if not g.seating_assignment and g.rsvp_status != "declined"
        ),
        "purchases": sum(1 for item in shopping if item.status not in {"purchased", "cancelled"}),
        "shopping_spent": sum(
            (item.total_actual for item in shopping if item.status == "purchased"), Decimal("0")
        ),
        "budget_paid": sum(
            (item.paid_amount or Decimal("0") for item in budget if item.status != "cancelled"),
            Decimal("0"),
        ),
    }
    return render_template("dashboard/index.html", wedding=wedding, metrics=metrics)


@dashboard_bp.get("/health")
def health():
    return {"status": "ok"}, 200
