from __future__ import annotations

from datetime import UTC, datetime

from app.extensions import db


class Family(db.Model):
    __tablename__ = "families"

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    wedding = db.relationship("Wedding", back_populates="families")
    guests = db.relationship("Guest", back_populates="family", lazy="selectin")
