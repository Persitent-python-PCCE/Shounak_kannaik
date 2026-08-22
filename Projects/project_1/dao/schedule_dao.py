"""
EventSchedule Data Access Object (DAO).

This class is the ONLY place allowed to execute database queries (db.session,
Model.query, etc.) related to EventSchedule entities.
"""

from models.schedule import EventSchedule
from config.database import db


class ScheduleDAO:
    """
    DAO handling database interactions for EventSchedule records.
    Holds no constructor arguments and interacts directly with the global db instance.
    """

    def get_all_schedules(self):
        """Fetch all event schedules from the database."""
        return db.session.execute(db.select(EventSchedule)).scalars().all()

    def get_by_id(self, schedule_id):
        """Fetch an event schedule by primary key ID."""
        return db.session.get(EventSchedule, schedule_id)

    def get_schedules_by_event_id(self, event_id):
        """Fetch all schedules for a specific event."""
        return db.session.execute(
            db.select(EventSchedule).where(EventSchedule.event_id == event_id)
        ).scalars().all()

    def get_schedules_by_venue_id(self, venue_id):
        """Fetch all schedules for a specific venue."""
        return db.session.execute(
            db.select(EventSchedule).where(EventSchedule.venue_id == venue_id)
        ).scalars().all()

    def create_schedule(self, schedule):
        """Persist a new EventSchedule record."""
        db.session.add(schedule)
        db.session.commit()
        return schedule

    def update_schedule(self, schedule):
        """Commit modifications made to an EventSchedule record."""
        db.session.commit()
        return schedule

    def delete_schedule(self, schedule):
        """Delete an EventSchedule record from the database."""
        db.session.delete(schedule)
        db.session.commit()
        return True

    def filter_schedules(self, filters: dict):
        """Filter event schedules by event_id, venue_id, status, or date range."""
        query = db.select(EventSchedule)
        if filters.get("event_id"):
            query = query.where(EventSchedule.event_id == filters["event_id"])
        if filters.get("venue_id"):
            query = query.where(EventSchedule.venue_id == filters["venue_id"])
        if filters.get("status"):
            query = query.where(EventSchedule.status.ilike(filters["status"]))
        if filters.get("from_date"):
            query = query.where(EventSchedule.start_datetime >= filters["from_date"])
        if filters.get("to_date"):
            query = query.where(EventSchedule.end_datetime <= filters["to_date"])

        return db.session.execute(query).scalars().all()
