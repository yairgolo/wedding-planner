from __future__ import annotations

from datetime import date, datetime, timezone

from app.extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    title = db.Column(db.String(220), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default="general", index=True)
    status = db.Column(db.String(30), nullable=False, default="todo", index=True)
    priority = db.Column(db.String(20), nullable=False, default="medium", index=True)
    due_date = db.Column(db.Date, nullable=True, index=True)
    assigned_to = db.Column(db.String(120), nullable=True, index=True)
    related_vendor_id = db.Column(
        db.Integer, db.ForeignKey("vendors.id"), nullable=True, index=True
    )
    notes = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
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

    wedding = db.relationship("Wedding", back_populates="tasks")
    related_vendor = db.relationship("Vendor")

    @property
    def is_completed(self) -> bool:
        return self.status == "done"

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_date and self.due_date < date.today() and not self.is_completed)

    @property
    def is_due_soon(self) -> bool:
        if not self.due_date or self.is_completed:
            return False
        days = (self.due_date - date.today()).days
        return 0 <= days <= 7

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def set_status(self, status: str) -> None:
        self.status = status
        self.completed_at = datetime.now(timezone.utc) if status == "done" else None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
