"""
Venue, Section, and Seat entity model definitions.
"""

from config.database import db


class Venue(db.Model):
    """
    Venue model representing physical event locations.
    """
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())

    sections = db.relationship("Section", back_populates="venue", cascade="all, delete-orphan")
    event_schedules = db.relationship("EventSchedule", back_populates="venue", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "capacity": self.capacity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Section(db.Model):
    """
    Section model representing distinct seating areas within a venue.
    """
    __tablename__ = "sections"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    venue = db.relationship("Venue", back_populates="sections")
    seats = db.relationship("Seat", back_populates="section", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "venue_id": self.venue_id,
            "name": self.name,
            "description": self.description,
        }


class Seat(db.Model):
    """
    Seat model representing individual assignable seats within a section.
    """
    __tablename__ = "seats"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, db.ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    row = db.Column(db.String(20), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    seat_type = db.Column(db.String(50), nullable=True, default="Regular")

    section = db.relationship("Section", back_populates="seats")
    booking_items = db.relationship("BookingItem", back_populates="seat")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "section_id": self.section_id,
            "row": self.row,
            "number": self.number,
            "seat_type": self.seat_type,
        }
