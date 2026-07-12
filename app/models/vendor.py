from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from app.extensions import db


class Vendor(db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default="other", index=True)
    contact_name = db.Column(db.String(180), nullable=True)
    phone = db.Column(db.String(40), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True)
    website_url = db.Column(db.String(600), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    agreed_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="considering", index=True)
    contract_signed = db.Column(db.Boolean, nullable=False, default=False)
    next_payment_date = db.Column(db.Date, nullable=True, index=True)
    arrival_time = db.Column(db.Time, nullable=True)
    rating = db.Column(db.Integer, nullable=False, default=0)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    wedding = db.relationship("Wedding", back_populates="vendors")
    budget_item = db.relationship(
        "BudgetItem",
        back_populates="vendor",
        uselist=False,
        foreign_keys="BudgetItem.vendor_id",
    )

    @property
    def balance(self) -> Decimal:
        return max(
            Decimal("0"),
            (self.agreed_amount or Decimal("0")) - (self.paid_amount or Decimal("0")),
        )

    @property
    def is_paid(self) -> bool:
        return self.balance == 0 and (self.agreed_amount or Decimal("0")) > 0

    @property
    def is_payment_overdue(self) -> bool:
        return bool(
            self.next_payment_date and self.next_payment_date < date.today() and self.balance > 0
        )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)
