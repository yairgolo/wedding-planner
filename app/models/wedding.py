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
    hebrew_date = db.Column(db.String(120), nullable=True)
    ceremony_time = db.Column(db.Time, nullable=True)
    waze_url = db.Column(db.String(600), nullable=True)
    venue_phone = db.Column(db.String(40), nullable=True)
    meal_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    venue_capacity = db.Column(db.Integer, nullable=False, default=0)
    max_tables = db.Column(db.Integer, nullable=False, default=0)
    public_base_url = db.Column(db.String(600), nullable=True)
    reminder_message = db.Column(db.Text, nullable=True)
    thank_you_message = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    budget_target = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    guests = db.relationship(
        "Guest", back_populates="wedding", lazy="dynamic", cascade="all, delete-orphan"
    )
    families = db.relationship(
        "Family", back_populates="wedding", lazy="selectin", cascade="all, delete-orphan"
    )
    seating_tables = db.relationship(
        "SeatingTable", back_populates="wedding", lazy="selectin", cascade="all, delete-orphan"
    )

    shopping_items = db.relationship(
        "ShoppingItem", back_populates="wedding", lazy="selectin", cascade="all, delete-orphan"
    )
    budget_items = db.relationship(
        "BudgetItem", back_populates="wedding", lazy="selectin", cascade="all, delete-orphan"
    )
    vendors = db.relationship(
        "Vendor", back_populates="wedding", lazy="selectin", cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "Task", back_populates="wedding", lazy="selectin", cascade="all, delete-orphan"
    )
    invitation_settings = db.relationship(
        "InvitationSettings",
        back_populates="wedding",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def display_name(self) -> str:
        return f"{self.partner_one} ו{self.partner_two}"

    @property
    def days_until(self) -> int | None:
        if not self.event_date:
            return None
        return (self.event_date - date.today()).days
