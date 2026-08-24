
from models.event import Event, EventType
from models.genre import Genre, event_genres
from config.database import db


class EventDAO:

    def get_all_events(self, page=None, per_page=None):
        """Fetch all events from the database with eager loaded relationships."""
        stmt = db.select(Event).options(
            db.joinedload(Event.event_type),
            db.selectinload(Event.genres)
        ).order_by(Event.id)
        if page is not None and per_page is not None:
            return db.paginate(stmt, page=page, per_page=per_page, error_out=False)
        return db.session.execute(stmt).scalars().all()

    def get_by_id(self, event_id):
        """Fetch an event by primary key ID with eager loaded relationships."""
        stmt = db.select(Event).options(
            db.joinedload(Event.event_type),
            db.selectinload(Event.genres)
        ).where(Event.id == event_id)
        return db.session.execute(stmt).scalar_one_or_none()


    def filter_events(self, filters: dict, page=None, per_page=None):
        """Filter events by name, event_type_id, genre_id, or age_rating with eager loaded relationships."""
        query = db.select(Event).options(
            db.joinedload(Event.event_type),
            db.selectinload(Event.genres)
        )
        if filters.get("name"):
            query = query.where(Event.name.ilike(f"%{filters['name']}%"))
        if filters.get("event_type_id"):
            query = query.where(Event.event_type_id == filters["event_type_id"])
        if filters.get("genre_id"):
            query = query.join(
                event_genres, Event.id == event_genres.c.event_id
            ).where(event_genres.c.genre_id == filters["genre_id"])
        if filters.get("age_rating"):
            query = query.where(Event.age_rating == filters["age_rating"])
        query = query.order_by(Event.id)
        if page is not None and per_page is not None:
            return db.paginate(query, page=page, per_page=per_page, error_out=False)
        return db.session.execute(query).scalars().all()


    def create_event(self, event):
        """Persist a new Event record."""
        db.session.add(event)
        db.session.commit()
        return event

    def update_event(self, event):
        """Commit modifications made to an Event record."""
        db.session.commit()
        return event

    def delete_event(self, event):
        """Delete an Event record from the database."""
        db.session.delete(event)
        db.session.commit()
        return True

    def get_all_event_types(self):
        """Fetch all event types."""
        return db.session.execute(db.select(EventType)).scalars().all()

    def get_event_type_by_id(self, type_id):
        """Fetch an event type by primary key ID."""
        return db.session.get(EventType, type_id)

    def get_all_genres(self):
        """Fetch all genres."""
        return db.session.execute(db.select(Genre)).scalars().all()

    def add_genre_to_event(self, event_id, genre_id):
        """Link a genre to an event via the ORM relationship."""
        event = db.session.get(Event, event_id)
        genre = db.session.get(Genre, genre_id)
        if event and genre and genre not in event.genres:
            event.genres.append(genre)
            db.session.commit()

    def set_genres_for_event(self, event_id, genre_ids: list):
        """Set or replace all genres associated with an event."""
        event = db.session.get(Event, event_id)
        if event:
            if genre_ids:
                stmt = db.select(Genre).where(Genre.id.in_(genre_ids))
                genres = db.session.execute(stmt).scalars().all()
                event.genres = list(genres)
            else:
                event.genres = []
            db.session.commit()

    def get_genres_for_event(self, event_id):
        """Fetch all genres associated with a specific event."""
        stmt = (
            db.select(Genre)
            .join(event_genres, Genre.id == event_genres.c.genre_id)
            .where(event_genres.c.event_id == event_id)
        )
        return db.session.execute(stmt).scalars().all()

    def get_trending_event_this_week(self):
        """Fetch the trending event with the most booked tickets in the last 7 days."""
        from models.booking import Booking, BookingItem
        from models.schedule import EventSchedule
        from datetime import datetime, timedelta, timezone

        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        stmt = (
            db.select(Event.id, db.func.count(BookingItem.id).label("ticket_count"))
            .join(EventSchedule, Event.id == EventSchedule.event_id)
            .join(Booking, EventSchedule.id == Booking.schedule_id)
            .join(BookingItem, Booking.id == BookingItem.booking_id)
            .where(Booking.created_at >= one_week_ago)
            .group_by(Event.id)
            .order_by(db.desc("ticket_count"))
            .limit(1)
        )
        row = db.session.execute(stmt).first()
        if row:
            return self.get_by_id(row[0])
        return None
