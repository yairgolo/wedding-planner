from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class InvitationSettings(db.Model):
    __tablename__ = "invitation_settings"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(
        db.Integer, db.ForeignKey("weddings.id"), nullable=False, unique=True, index=True
    )
    message_template = db.Column(db.Text, nullable=False, default="")
    image_filename = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    wedding = db.relationship("Wedding", back_populates="invitation_settings")


class InvitationActivity(db.Model):
    __tablename__ = "invitation_activities"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    guest_id = db.Column(db.Integer, db.ForeignKey("guests.id"), nullable=False, index=True)
    activity_type = db.Column(db.String(30), nullable=False, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    guest = db.relationship("Guest")
