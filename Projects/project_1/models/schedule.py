
from config.database import db


class EventSchedule(db.Model):
    __tablename__ = "event_schedules"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    start_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    end_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(50), default="Scheduled")
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())

    event = db.relationship("Event", back_populates="event_schedules")
    venue = db.relationship("Venue", back_populates="event_schedules")
    bookings = db.relationship("Booking", back_populates="schedule", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "venue_id": self.venue_id,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "end_datetime": self.end_datetime.isoformat() if self.end_datetime else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
