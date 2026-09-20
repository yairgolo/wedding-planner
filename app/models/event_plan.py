from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class EventScheduleItem(db.Model):
    __tablename__ = "event_schedule_items"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    time = db.Column(db.Time, nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    owner = db.Column(db.String(180), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class MusicRequest(db.Model):
    __tablename__ = "music_requests"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    artist = db.Column(db.String(180), nullable=True)
    moment = db.Column(db.String(30), nullable=False, default="party", index=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
