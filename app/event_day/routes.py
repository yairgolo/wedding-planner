from __future__ import annotations

from datetime import date

from flask import Blueprint, abort, render_template, request
from flask_login import login_required
from sqlalchemy import or_

from app.extensions import db
from app.models import Guest, Task, Vendor, Wedding

event_day_bp = Blueprint("event_day", __name__, url_prefix="/event-day")


def current_wedding() -> Wedding:
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    if not wedding:
        abort(404)
    return wedding


@event_day_bp.get("")
@login_required
def index():
    wedding = current_wedding()
    query = request.args.get("q", "").strip()

    guests = []
    if query:
        pattern = f"%{query}%"
        guests = db.session.scalars(
            db.select(Guest)
            .where(
                Guest.wedding_id == wedding.id,
                Guest.deleted_at.is_(None),
                or_(
                    Guest.first_name.ilike(pattern),
                    Guest.last_name.ilike(pattern),
                    Guest.phone.ilike(pattern),
                ),
            )
            .order_by(Guest.last_name, Guest.first_name)
            .limit(20)
        ).all()

    vendors = db.session.scalars(
        db.select(Vendor)
        .where(
            Vendor.wedding_id == wedding.id,
            Vendor.deleted_at.is_(None),
            Vendor.status.in_(["booked", "completed"]),
        )
        .order_by(Vendor.arrival_time.is_(None), Vendor.arrival_time, Vendor.name)
    ).all()

    tasks = db.session.scalars(
        db.select(Task)
        .where(
            Task.wedding_id == wedding.id,
            Task.deleted_at.is_(None),
            Task.status != "done",
            or_(
                Task.category == "wedding",
                Task.due_date == wedding.event_date,
                Task.due_date == date.today(),
            ),
        )
        .order_by(Task.priority == "urgent", Task.due_date.is_(None), Task.due_date)
        .limit(18)
    ).all()

    timeline = []
    if wedding.ceremony_time:
        timeline.append(
            {
                "time": wedding.ceremony_time,
                "title": "חופה",
                "subtitle": wedding.venue_name or "האירוע",
                "icon": "💍",
            }
        )
    for vendor in vendors:
        if vendor.arrival_time:
            timeline.append(
                {
                    "time": vendor.arrival_time,
                    "title": vendor.name,
                    "subtitle": "הגעת ספק",
                    "icon": "🤝",
                }
            )
    timeline.sort(key=lambda item: item["time"])

    return render_template(
        "event_day/index.html",
        wedding=wedding,
        guests=guests,
        query=query,
        vendors=vendors,
        tasks=tasks,
        timeline=timeline,
    )
