"""
BookingStatus, Booking, and BookingItem entity model definitions.
"""

from datetime import datetime, timezone
import uuid
from config.database import db


class BookingStatus(db.Model):
    """
    BookingStatus model representing status values for bookings (e.g., Pending, Confirmed, Cancelled).
    """
    __tablename__ = "booking_statuses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(50), unique=True, nullable=False)

    bookings = db.relationship("Booking", back_populates="booking_status")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "status_name": self.status_name,
        }


class Booking(db.Model):
    """
    Booking model representing a user's ticket reservation transaction.
    """
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_reference = db.Column(db.String(100), unique=True, nullable=True, default=lambda: str(uuid.uuid4())[:8].upper())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("event_schedules.id"), nullable=True)
    payment_mode_id = db.Column(db.Integer, db.ForeignKey("payment_modes.id"), nullable=True)
    payment_status_id = db.Column(db.Integer, db.ForeignKey("payment_statuses.id"), nullable=True)
    booking_status_id = db.Column(db.Integer, db.ForeignKey("booking_statuses.id"), nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship("User", back_populates="bookings")
    schedule = db.relationship("EventSchedule", back_populates="bookings")
    payment_mode = db.relationship("PaymentMode", back_populates="bookings")
    payment_status = db.relationship("PaymentStatus", back_populates="bookings")
    booking_status = db.relationship("BookingStatus", back_populates="bookings")
    booking_items = db.relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")
    transactions = db.relationship("PaymentTransaction", back_populates="booking", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "booking_reference": self.booking_reference,
            "user_id": self.user_id,
            "schedule_id": self.schedule_id,
            "payment_mode_id": self.payment_mode_id,
            "payment_status_id": self.payment_status_id,
            "booking_status_id": self.booking_status_id,
            "total_amount": float(self.total_amount) if self.total_amount is not None else 0.00,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BookingItem(db.Model):
    """
    BookingItem model representing individual reserved seats/tickets under a booking.
    """
    __tablename__ = "booking_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())

    # Relationships
    booking = db.relationship("Booking", back_populates="booking_items")
    seat = db.relationship("Seat", back_populates="booking_items")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "seat_id": self.seat_id,
            "price": float(self.price) if self.price is not None else 0.00,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
