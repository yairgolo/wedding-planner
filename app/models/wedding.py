from __future__ import annotations

from datetime import UTC, date, datetime

from app.extensions import db


class Wedding(db.Model):
    __tablename__ = "weddings"

    id = db.Column(db.Integer, primary_key=True)
    partner_one = db.Column(db.String(100), nullable=False)
    partner_two = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.Date, nullable=True)
    venue_name = db.Column(db.String(180), nullable=True)
    venue_address = db.Column(db.String(255), nullable=True)
    budget_target = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    @property
    def display_name(self) -> str:
        return f"{self.partner_one} ו{self.partner_two}"

    @property
    def days_until(self) -> int | None:
        if not self.event_date:
            return None
        return (self.event_date - date.today()).days
