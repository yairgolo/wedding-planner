from decimal import Decimal

from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models import (
    AuditLog,
    BudgetItem,
    Document,
    Gift,
    Guest,
    ShoppingItem,
    Task,
    Vendor,
    Wedding,
)


dashboard_bp = Blueprint("dashboard", __name__)


def percent(done: int | Decimal, total: int | Decimal) -> int:
    """Return a safe rounded percentage between 0 and 100."""
    if not total:
        return 0
    return max(0, min(100, round((float(done) / float(total)) * 100)))


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
    recent_activity = []

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
        recent_activity = db.session.scalars(
            db.select(AuditLog)
            .where(AuditLog.wedding_id == wedding.id)
            .order_by(AuditLog.created_at.desc())
            .limit(7)
        ).all()

    invited = sum(g.invited_count for g in guests)
    confirmed = sum(g.confirmed_count for g in guests if g.rsvp_status == "confirmed")
    pending = sum(g.invited_count for g in guests if g.rsvp_status in {"pending", "maybe"})
    declined = sum(g.invited_count for g in guests if g.rsvp_status == "declined")
    invitation_unsent = sum(g.invited_count for g in guests if not g.invitation_sent)
    seated = sum(
        g.confirmed_count if g.confirmed_count else g.invited_count
        for g in guests
        if g.seating_assignment and g.rsvp_status != "declined"
    )
    unseated = sum(
        g.confirmed_count if g.rsvp_status == "confirmed" and g.confirmed_count else g.invited_count
        for g in guests
        if not g.seating_assignment and g.rsvp_status != "declined"
    )
    open_tasks = sum(1 for task in tasks if task.status != "done")
    completed_tasks = sum(1 for task in tasks if task.status == "done")
    overdue_tasks = sum(1 for task in tasks if task.is_overdue)
    open_purchases = sum(1 for item in shopping if item.status not in {"purchased", "cancelled"})
    purchased = sum(1 for item in shopping if item.status == "purchased")
    shopping_spent = sum(
        (item.total_actual for item in shopping if item.status == "purchased"), Decimal("0")
    )
    budget_committed = sum(
        (item.committed_amount for item in budget if item.status != "cancelled"), Decimal("0")
    )
    budget_paid = sum(
        (item.paid_amount or Decimal("0") for item in budget if item.status != "cancelled"),
        Decimal("0"),
    )
    vendor_balance = sum(
        (vendor.balance for vendor in vendors if vendor.status != "cancelled"), Decimal("0")
    )
    signed_vendors = sum(1 for vendor in vendors if vendor.contract_signed)
    unsigned_contracts = sum(
        1
        for vendor in vendors
        if vendor.status in {"booked", "completed"} and not vendor.contract_signed
    )

    metrics = {
        "guests": invited,
        "confirmed": confirmed,
        "pending": pending,
        "declined": declined,
        "invitation_unsent": invitation_unsent,
        "seated": seated,
        "unseated": unseated,
        "tasks": open_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "purchases": open_purchases,
        "purchased": purchased,
        "shopping_spent": shopping_spent,
        "budget_committed": budget_committed,
        "budget_paid": budget_paid,
        "budget_balance": max(Decimal("0"), budget_committed - budget_paid),
        "vendors": len(vendors),
        "signed_vendors": signed_vendors,
        "vendor_balance": vendor_balance,
        "gifts": len(gifts),
        "gift_total": sum((gift.value for gift in gifts), Decimal("0")),
        "thank_you_pending": sum(1 for gift in gifts if not gift.thank_you_sent),
        "documents": len(documents),
        "unsigned_contracts": unsigned_contracts,
    }

    readiness_details = [
        ("תאריך חתונה", bool(wedding and wedding.event_date), "settings.wedding_profile"),
        ("אולם וכתובת", bool(wedding and wedding.venue_name and wedding.venue_address), "settings.wedding_profile"),
        ("רשימת מוזמנים", invited > 0, "guests.index"),
        ("שליחת הזמנות", invited > 0 and invitation_unsent == 0, "invitations.index"),
        ("אישורי הגעה", invited > 0 and pending == 0, "guests.index"),
        ("הושבה", confirmed > 0 and unseated == 0, "seating.index"),
        ("אין משימות באיחור", overdue_tasks == 0, "tasks.index"),
        ("חוזי ספקים", bool(vendors) and unsigned_contracts == 0, "vendors.index"),
    ]
    health_score = round(
        (sum(1 for _label, complete, _endpoint in readiness_details if complete) / len(readiness_details))
        * 100
    )

    module_progress = [
        ("מוזמנים", percent(confirmed + declined, invited), "guests.index"),
        ("הזמנות", percent(invited - invitation_unsent, invited), "invitations.index"),
        ("הושבה", percent(seated, seated + unseated), "seating.index"),
        ("משימות", percent(completed_tasks, len(tasks)), "tasks.index"),
        ("ספקים", percent(signed_vendors, len(vendors)), "vendors.index"),
        ("קניות", percent(purchased, len(shopping)), "shopping.index"),
    ]

    attention_items = []
    if invitation_unsent:
        attention_items.append(("💌", f"לשלוח הזמנה ל־{invitation_unsent} מוזמנים", "invitations.index"))
    if pending:
        attention_items.append(("⏳", f"{pending} מוזמנים עדיין לא אישרו", "guests.index"))
    if unseated:
        attention_items.append(("🪑", f"{unseated} אורחים עדיין ללא שולחן", "seating.index"))
    if overdue_tasks:
        attention_items.append(("📋", f"{overdue_tasks} משימות באיחור", "tasks.index"))
    if vendor_balance:
        attention_items.append(
            ("💰", f"נותרו ₪{float(vendor_balance):,.0f} לתשלום לספקים", "vendors.index")
        )

    urgent_tasks = sorted(
        [task for task in tasks if task.status != "done"],
        key=lambda task: (task.due_date is None, task.due_date, task.priority != "urgent"),
    )[:5]

    return render_template(
        "dashboard/index.html",
        wedding=wedding,
        metrics=metrics,
        urgent_tasks=urgent_tasks,
        health_score=health_score,
        readiness_details=readiness_details,
        module_progress=module_progress,
        attention_items=attention_items[:5],
        recent_activity=recent_activity,
    )


@dashboard_bp.get("/health")
def health():
    return {"status": "ok"}, 200
