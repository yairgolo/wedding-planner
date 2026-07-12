from decimal import Decimal

from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models import BudgetItem, Document, Gift, Guest, ShoppingItem, Task, Vendor, Wedding

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    guests = []
    shopping = []
    budget = []
    tasks = []
    vendors = []
    gifts = []
    documents = []
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
        tasks = db.session.scalars(
            db.select(Task).where(Task.wedding_id == wedding.id, Task.deleted_at.is_(None))
        ).all()
        gifts = db.session.scalars(
            db.select(Gift).where(Gift.wedding_id == wedding.id, Gift.deleted_at.is_(None))
        ).all()
        documents = db.session.scalars(
            db.select(Document).where(
                Document.wedding_id == wedding.id, Document.deleted_at.is_(None)
            )
        ).all()
        vendors = db.session.scalars(
            db.select(Vendor).where(Vendor.wedding_id == wedding.id, Vendor.deleted_at.is_(None))
        ).all()
    metrics = {
        "guests": sum(g.invited_count for g in guests),
        "confirmed": sum(g.confirmed_count for g in guests if g.rsvp_status == "confirmed"),
        "pending": sum(g.invited_count for g in guests if g.rsvp_status in {"pending", "maybe"}),
        "declined": sum(g.invited_count for g in guests if g.rsvp_status == "declined"),
        "tasks": sum(1 for task in tasks if task.status != "done"),
        "overdue_tasks": sum(1 for task in tasks if task.is_overdue),
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
        "vendors": len(vendors),
        "vendor_balance": sum(
            (vendor.balance for vendor in vendors if vendor.status != "cancelled"), Decimal("0")
        ),
        "gifts": len(gifts),
        "gift_total": sum((gift.value for gift in gifts), Decimal("0")),
        "thank_you_pending": sum(1 for gift in gifts if not gift.thank_you_sent),
        "documents": len(documents),
        "unsigned_contracts": sum(
            1
            for vendor in vendors
            if vendor.status in {"booked", "completed"} and not vendor.contract_signed
        ),
    }
    urgent_tasks = sorted(
        [task for task in tasks if task.status != "done"],
        key=lambda task: (task.due_date is None, task.due_date, task.priority != "urgent"),
    )[:5]
    return render_template(
        "dashboard/index.html", wedding=wedding, metrics=metrics, urgent_tasks=urgent_tasks
    )


@dashboard_bp.get("/health")
def health():
    return {"status": "ok"}, 200
