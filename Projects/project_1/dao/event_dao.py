"""
Event Data Access Object (DAO).

This class is the ONLY place allowed to execute database queries (db.session,
Model.query, etc.) related to Event entities.
"""

from models.event import Event, EventType
from models.genre import Genre, event_genres
from config.database import db


class EventDAO:
    """
    DAO handling database interactions for Event, EventType, Genre, and EventGenre junction records.
    Holds no constructor arguments and interacts directly with the global db instance.
    """

    def get_all_events(self):
        """Fetch all events from the database."""
        return db.session.execute(db.select(Event)).scalars().all()

    def get_by_id(self, event_id):
        """Fetch an event by primary key ID."""
        return db.session.get(Event, event_id)

    def filter_events(self, filters: dict):
        """Filter events by name, event_type_id, genre_id, or age_rating."""
        query = db.select(Event)
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

    def get_genres_for_event(self, event_id):
        """Fetch all genres associated with a specific event."""
        stmt = (
            db.select(Genre)
            .join(event_genres, Genre.id == event_genres.c.genre_id)
            .where(event_genres.c.event_id == event_id)
        )
        return db.session.execute(stmt).scalars().all()
