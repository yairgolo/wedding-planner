from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db


class Gift(db.Model):
    __tablename__ = "gifts"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    guest_name = db.Column(db.String(180), nullable=False, index=True)
    gift_type = db.Column(db.String(30), nullable=False, default="cash", index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    description = db.Column(db.String(500), nullable=True)
    received_date = db.Column(db.Date, nullable=True, index=True)
    thank_you_sent = db.Column(db.Boolean, nullable=False, default=False, index=True)
    thank_you_sent_at = db.Column(db.DateTime(timezone=True), nullable=True)
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

    @property
    def value(self) -> Decimal:
        return self.amount or Decimal("0")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None
