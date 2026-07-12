from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class SeatingTable(db.Model):
    __tablename__ = "seating_tables"
    __table_args__ = (
        db.UniqueConstraint("wedding_id", "number", name="uq_seating_table_wedding_number"),
    )

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    number = db.Column(db.String(30), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=10)
    shape = db.Column(db.String(20), nullable=False, default="round")
    zone = db.Column(db.String(80), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    position_x = db.Column(db.Integer, nullable=False, default=0)
    position_y = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    wedding = db.relationship("Wedding", back_populates="seating_tables")
    assignments = db.relationship(
        "SeatingAssignment",
        back_populates="table",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def display_name(self) -> str:
        return self.name or f"שולחן {self.number}"

    @property
    def occupied_seats(self) -> int:
        return sum(assignment.seat_count for assignment in self.assignments)

    @property
    def available_seats(self) -> int:
        return max(self.capacity - self.occupied_seats, 0)

    @property
    def occupancy_percent(self) -> int:
        if not self.capacity:
            return 0
        return min(round((self.occupied_seats / self.capacity) * 100), 100)


class SeatingAssignment(db.Model):
    __tablename__ = "seating_assignments"
    __table_args__ = (
        db.UniqueConstraint("wedding_id", "guest_id", name="uq_seating_assignment_guest"),
    )

    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey("weddings.id"), nullable=False, index=True)
    table_id = db.Column(
        db.Integer,
        db.ForeignKey("seating_tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    guest_id = db.Column(db.Integer, db.ForeignKey("guests.id"), nullable=False, index=True)
    seat_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    table = db.relationship("SeatingTable", back_populates="assignments")
    guest = db.relationship("Guest", back_populates="seating_assignment")
