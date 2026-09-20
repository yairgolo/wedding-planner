from __future__ import annotations

from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from app.extensions import db
from app.models import EventScheduleItem, Guest, MusicRequest, Task, Vendor, Wedding

from .forms import MusicRequestForm, ScheduleItemForm

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

    schedule_items = db.session.scalars(
        db.select(EventScheduleItem)
        .where(EventScheduleItem.wedding_id == wedding.id)
        .order_by(EventScheduleItem.time, EventScheduleItem.id)
    ).all()
    music_items = db.session.scalars(
        db.select(MusicRequest)
        .where(MusicRequest.wedding_id == wedding.id)
        .order_by(MusicRequest.moment, MusicRequest.created_at)
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
        schedule_items=schedule_items,
        music_items=music_items,
        schedule_form=ScheduleItemForm(prefix="schedule"),
        music_form=MusicRequestForm(prefix="music"),
    )


@event_day_bp.post("/schedule")
@login_required
def add_schedule_item():
    wedding = current_wedding()
    form = ScheduleItemForm(prefix="schedule")
    if form.validate_on_submit():
        db.session.add(EventScheduleItem(
            wedding_id=wedding.id,
            time=form.time.data,
            title=form.title.data.strip(),
            owner=(form.owner.data or "").strip() or None,
            notes=(form.notes.data or "").strip() or None,
        ))
        db.session.commit()
        flash("הפריט נוסף ללוח הזמנים.", "success")
    else:
        flash("יש למלא שעה ותיאור קצר.", "danger")
    return redirect(url_for("event_day.index"))


@event_day_bp.post("/schedule/<int:item_id>/delete")
@login_required
def delete_schedule_item(item_id: int):
    wedding = current_wedding()
    item = db.get_or_404(EventScheduleItem, item_id)
    if item.wedding_id != wedding.id:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash("הפריט הוסר מלוח הזמנים.", "success")
    return redirect(url_for("event_day.index"))


@event_day_bp.post("/music")
@login_required
def add_music_request():
    wedding = current_wedding()
    form = MusicRequestForm(prefix="music")
    if form.validate_on_submit():
        db.session.add(MusicRequest(
            wedding_id=wedding.id,
            title=form.title.data.strip(),
            artist=(form.artist.data or "").strip() or None,
            moment=form.moment.data,
            notes=(form.notes.data or "").strip() or None,
        ))
        db.session.commit()
        flash("השיר נוסף לפלייליסט.", "success")
    else:
        flash("יש למלא שם שיר או אמן.", "danger")
    return redirect(url_for("event_day.index"))


@event_day_bp.post("/music/<int:item_id>/delete")
@login_required
def delete_music_request(item_id: int):
    wedding = current_wedding()
    item = db.get_or_404(MusicRequest, item_id)
    if item.wedding_id != wedding.id:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash("השיר הוסר מהפלייליסט.", "success")
    return redirect(url_for("event_day.index"))
