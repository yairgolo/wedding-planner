from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default="other", index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    mime_type = db.Column(db.String(120), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False, default=0)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True, index=True)
    notes = db.Column(db.Text, nullable=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None
