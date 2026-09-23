from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone

from app.extensions import db


def _now() -> datetime:
    return datetime.now(timezone.utc)


class InvitationPortalSettings(db.Model):
    __tablename__ = "invitation_portal_settings"

    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)


class InvitationSender(db.Model):
    __tablename__ = "invitation_senders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    side = db.Column(db.String(20), nullable=False, index=True)
    access_token = db.Column(
        db.String(64),
        nullable=False,
        unique=True,
        default=lambda: secrets.token_urlsafe(32),
        index=True,
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    male_template = db.Column(db.Text, nullable=False)
    female_template = db.Column(db.Text, nullable=False)
    plural_template = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)


class InvitationPortalGuest(db.Model):
    __tablename__ = "invitation_portal_guests"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(
        db.String(36), nullable=False, unique=True, default=lambda: str(uuid.uuid4()), index=True
    )
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(32), nullable=True, index=True)
    side = db.Column(db.String(20), nullable=False, index=True)
    salutation = db.Column(db.String(10), nullable=False, index=True)
    group_name = db.Column(db.String(120), nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default="unsent", index=True)
    last_sender_id = db.Column(db.Integer, db.ForeignKey("invitation_senders.id"), nullable=True)
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    last_sender = db.relationship("InvitationSender")

    @property
    def full_name(self) -> str:
        return " ".join(part for part in (self.first_name, self.last_name) if part).strip()


class InvitationPortalActivity(db.Model):
    __tablename__ = "invitation_portal_activities"

    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(
        db.Integer, db.ForeignKey("invitation_portal_guests.id"), nullable=False, index=True
    )
    sender_id = db.Column(
        db.Integer, db.ForeignKey("invitation_senders.id"), nullable=True, index=True
    )
    action = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)

    guest = db.relationship("InvitationPortalGuest")
    sender = db.relationship("InvitationSender")


class InvitationSendAttempt(db.Model):
    """One explicit send operation, resumable after returning from the phone share sheet."""

    __tablename__ = "invitation_send_attempts"
    id = db.Column(db.String(64), primary_key=True, default=lambda: secrets.token_urlsafe(24))
    guest_id = db.Column(
        db.Integer, db.ForeignKey("invitation_portal_guests.id"), nullable=False, index=True
    )
    sender_id = db.Column(db.Integer, db.ForeignKey("invitation_senders.id"), nullable=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    prior_status = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False, default="pending", index=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)

    sender = db.relationship("InvitationSender")
