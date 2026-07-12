from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from app.extensions import db


class ShoppingItem(db.Model):
    __tablename__ = "shopping_items"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    category = db.Column(db.String(30), nullable=False, default="wedding", index=True)
    status = db.Column(db.String(30), nullable=False, default="planned", index=True)
    priority = db.Column(db.String(20), nullable=False, default="medium", index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    estimated_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    actual_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    store_name = db.Column(db.String(180), nullable=True)
    product_url = db.Column(db.String(600), nullable=True)
    due_date = db.Column(db.Date, nullable=True, index=True)
    purchased_at = db.Column(db.DateTime(timezone=True), nullable=True)
    is_wishlist = db.Column(db.Boolean, nullable=False, default=False, index=True)
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

    wedding = db.relationship("Wedding", back_populates="shopping_items")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def total_estimated(self) -> Decimal:
        return (self.estimated_price or Decimal("0")) * self.quantity

    @property
    def total_actual(self) -> Decimal:
        return (self.actual_price or Decimal("0")) * self.quantity

    @property
    def is_purchased(self) -> bool:
        return self.status == "purchased"

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_date and self.due_date < date.today() and not self.is_purchased)

    def mark_purchased(self) -> None:
        self.status = "purchased"
        self.purchased_at = datetime.now(timezone.utc)
        if not self.actual_price:
            self.actual_price = self.estimated_price

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
