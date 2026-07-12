from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Guest(db.Model):
    __tablename__ = "guests"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True
    )
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    family_id = db.Column(db.Integer, db.ForeignKey("families.id"), nullable=True, index=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(32), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True, index=True)
    side = db.Column(db.String(20), nullable=False, default="shared", index=True)
    group_name = db.Column(db.String(100), nullable=True, index=True)

    invited_count = db.Column(db.Integer, nullable=False, default=1)
    confirmed_count = db.Column(db.Integer, nullable=False, default=0)
    rsvp_status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    rsvp_token = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        default=lambda: secrets.token_urlsafe(32),
        index=True,
    )
    rsvp_message = db.Column(db.Text, nullable=True)
    rsvp_updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    invitation_sent = db.Column(db.Boolean, nullable=False, default=False, index=True)
    invitation_sent_at = db.Column(db.DateTime(timezone=True), nullable=True)
    invitation_attempts = db.Column(db.Integer, nullable=False, default=0)

    is_vip = db.Column(db.Boolean, nullable=False, default=False, index=True)
    diet = db.Column(db.String(40), nullable=False, default="regular")
    diet_notes = db.Column(db.String(255), nullable=True)
    table_number = db.Column(db.String(30), nullable=True, index=True)
    notes = db.Column(db.Text, nullable=True)

    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    wedding = db.relationship("Wedding", back_populates="guests")
    family = db.relationship("Family", back_populates="guests")
    seating_assignment = db.relationship(
        "SeatingAssignment", back_populates="guest", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return " ".join(part for part in (self.first_name, self.last_name) if part).strip()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None
