from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from app.extensions import db


class BudgetItem(db.Model):
    __tablename__ = "budget_items"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False, default="other", index=True)
    supplier_name = db.Column(db.String(180), nullable=True)
    planned_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    actual_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="planned", index=True)
    due_date = db.Column(db.Date, nullable=True, index=True)
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

    wedding = db.relationship("Wedding", back_populates="budget_items")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def committed_amount(self) -> Decimal:
        actual = self.actual_amount or Decimal("0")
        planned = self.planned_amount or Decimal("0")
        return actual if actual > 0 else planned

    @property
    def balance(self) -> Decimal:
        return max(Decimal("0"), self.committed_amount - (self.paid_amount or Decimal("0")))

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_date and self.due_date < date.today() and self.balance > 0)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)
