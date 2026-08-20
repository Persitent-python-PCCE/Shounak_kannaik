"""
EventType and Event entity model definitions.
"""

from config.database import db
from models.genre import event_genres


class EventType(db.Model):
    """
    EventType model representing categories of events (e.g., Concert, Movie, Play).
    """
    __tablename__ = "event_types"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    events = db.relationship("Event", back_populates = "event_type")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "type_name": self.type_name,
            "description": self.description,
        }


class Event(db.Model):
    """
    Event model representing bookable events/shows.
    """
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    about = db.Column(db.Text, nullable=True)
    event_type_id = db.Column(db.Integer, db.ForeignKey("event_types.id", ondelete="SET NULL"), nullable=True)
    age_rating = db.Column(db.String(20), nullable=True)
    poster_image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now())

    genres = db.relationship("Genre", secondary = event_genres, back_populates = "events")
    event_type = db.relationship("EventType", back_populates="events")
    event_schedules = db.relationship("EventSchedule", back_populates="event", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize model instance to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "about": self.about,
            "event_type_id": self.event_type_id,
            "age_rating": self.age_rating,
            "poster_image_path": self.poster_image_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
