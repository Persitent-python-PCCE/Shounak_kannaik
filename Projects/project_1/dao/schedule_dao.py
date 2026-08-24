
from models.schedule import EventSchedule
from models.venue import Venue, Section, Seat
from models.event import Event
from config.database import db


class ScheduleDAO:

    def _schedule_options(self):
        return [
            db.joinedload(EventSchedule.event),
            db.joinedload(EventSchedule.venue).selectinload(Venue.sections).selectinload(Section.seats)
        ]

    def get_all_schedules(self):
        """Fetch all event schedules from the database."""
        stmt = db.select(EventSchedule).options(*self._schedule_options())
        return db.session.execute(stmt).scalars().all()

    def get_by_id(self, schedule_id):
        """Fetch an event schedule by primary key ID."""
        stmt = db.select(EventSchedule).options(*self._schedule_options()).where(EventSchedule.id == schedule_id)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_schedules_by_event_id(self, event_id):
        """Fetch all schedules for a specific event."""
        stmt = db.select(EventSchedule).options(*self._schedule_options()).where(EventSchedule.event_id == event_id)
        return db.session.execute(stmt).scalars().all()

    def get_schedules_by_venue_id(self, venue_id):
        """Fetch all schedules for a specific venue."""
        stmt = db.select(EventSchedule).options(*self._schedule_options()).where(EventSchedule.venue_id == venue_id)
        return db.session.execute(stmt).scalars().all()


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
        query = db.select(EventSchedule).options(*self._schedule_options())
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
