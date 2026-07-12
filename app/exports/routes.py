import csv
from io import StringIO

from flask import Blueprint, Response, render_template
from flask_login import login_required

from app.extensions import db
from app.models import Gift, Guest, ShoppingItem, Task, Vendor, Wedding

exports_bp = Blueprint("exports", __name__, url_prefix="/exports")


@exports_bp.get("")
@login_required
def index():
    return render_template("exports/index.html")


def csv_response(filename, headers, rows):
    output = StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@exports_bp.get("/<module>/csv")
@login_required
def module_csv(module):
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    if not wedding:
        return csv_response("empty.csv", ["אין נתונים"], [])
    if module == "guests":
        items = db.session.scalars(
            db.select(Guest).where(Guest.wedding_id == wedding.id, Guest.deleted_at.is_(None))
        ).all()
        return csv_response(
            "guests.csv",
            ["שם", "טלפון", "צד", "מוזמנים", "אישרו", "סטטוס", "שולחן"],
            [
                [
                    g.full_name,
                    g.phone or "",
                    g.side,
                    g.invited_count,
                    g.confirmed_count,
                    g.rsvp_status,
                    g.table_number or "",
                ]
                for g in items
            ],
        )
    if module == "vendors":
        items = db.session.scalars(
            db.select(Vendor).where(Vendor.wedding_id == wedding.id, Vendor.deleted_at.is_(None))
        ).all()
        return csv_response(
            "vendors.csv",
            ["ספק", "קטגוריה", "טלפון", "סכום", "שולם", "יתרה", "חוזה"],
            [
                [
                    v.name,
                    v.category,
                    v.phone or "",
                    v.agreed_amount,
                    v.paid_amount,
                    v.balance,
                    "כן" if v.contract_signed else "לא",
                ]
                for v in items
            ],
        )
    if module == "tasks":
        items = db.session.scalars(
            db.select(Task).where(Task.wedding_id == wedding.id, Task.deleted_at.is_(None))
        ).all()
        return csv_response(
            "tasks.csv",
            ["משימה", "סטטוס", "עדיפות", "אחראי", "תאריך יעד"],
            [[t.title, t.status, t.priority, t.assigned_to or "", t.due_date or ""] for t in items],
        )
    if module == "shopping":
        items = db.session.scalars(
            db.select(ShoppingItem).where(
                ShoppingItem.wedding_id == wedding.id, ShoppingItem.deleted_at.is_(None)
            )
        ).all()
        return csv_response(
            "shopping.csv",
            ["פריט", "קטגוריה", "סטטוס", "כמות", "מחיר משוער", "מחיר בפועל", "חנות"],
            [
                [
                    i.name,
                    i.category,
                    i.status,
                    i.quantity,
                    i.estimated_price,
                    i.actual_price,
                    i.store_name or "",
                ]
                for i in items
            ],
        )
    if module == "gifts":
        items = db.session.scalars(
            db.select(Gift).where(Gift.wedding_id == wedding.id, Gift.deleted_at.is_(None))
        ).all()
        return csv_response(
            "gifts.csv",
            ["שם", "סוג", "סכום", "תאריך", "תודה נשלחה"],
            [
                [
                    g.guest_name,
                    g.gift_type,
                    g.amount,
                    g.received_date or "",
                    "כן" if g.thank_you_sent else "לא",
                ]
                for g in items
            ],
        )
    return csv_response("unknown.csv", ["מודול לא מוכר"], [])
