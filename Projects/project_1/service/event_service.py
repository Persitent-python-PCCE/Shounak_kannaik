"""
Event Service.

Handles business logic for event discovery, scheduling, catalog management, and administrative CRUD.
Receives EventDAO via constructor injection to facilitate unit testing with mock DAOs.
"""

from models.event import Event


class EventService:
    """
    Service layer handling event operations.
    """

    def __init__(self, event_dao):
        """
        Constructor injection of the EventDAO dependency.

        :param event_dao: EventDAO instance (or fake/mock DAO in tests)
        """
        self.event_dao = event_dao

    def get_all_events(self):
        """Retrieve all available events."""
        return self.event_dao.get_all_events()

    def get_event_by_id(self, event_id):
        """Retrieve an event by ID."""
        event = self.event_dao.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found.")
        return event

    def filter_events(self, filters: dict):
        """Filter events with cleaned/validated parameters."""
        cleaned_filters = {}
        if filters.get("name"):
            cleaned_filters["name"] = filters.get("name").strip()
        if filters.get("event_type_id"):
            try:
                cleaned_filters["event_type_id"] = int(str(filters.get("event_type_id")).strip())
            except ValueError:
                raise ValueError("event_type_id must be a valid integer.")
        if filters.get("genre_id"):
            try:
                cleaned_filters["genre_id"] = int(str(filters.get("genre_id")).strip())
            except ValueError:
                raise ValueError("genre_id must be a valid integer.")
        if filters.get("age_rating"):
            cleaned_filters["age_rating"] = filters.get("age_rating").strip()

        return self.event_dao.filter_events(cleaned_filters)

    def get_all_event_types(self):
        """Retrieve all event types."""
        return self.event_dao.get_all_event_types()

    def get_all_genres(self):
        """Retrieve all genres."""
        return self.event_dao.get_all_genres()

    def get_genres_for_event(self, event_id):
        """Retrieve all genres associated with a specific event."""
        return self.event_dao.get_genres_for_event(event_id)

    def create_event(self, data):
        """Create and persist a new event."""
        if not data.get("name"):
            raise ValueError("Event name is required.")

        event = Event(
            name=data.get("name").strip(),
            about=data.get("about"),
            event_type_id=data.get("event_type_id"),
            age_rating=data.get("age_rating"),
            poster_image_path=data.get("poster_image_path"),
        )
        return self.event_dao.create_event(event)

    def update_event(self, data):
        """Update existing event details."""
        event_id = data.get("event_id")
        if not event_id:
            raise ValueError("event_id is required.")

        event = self.get_event_by_id(event_id)
        if "name" in data and data["name"]:
            event.name = data["name"].strip()
        if "about" in data:
            event.about = data["about"]
        if "event_type_id" in data:
            event.event_type_id = data["event_type_id"]
        if "age_rating" in data:
            event.age_rating = data["age_rating"]
        if "poster_image_path" in data:
            event.poster_image_path = data["poster_image_path"]

        return self.event_dao.update_event(event)

    def delete_event(self, event_id):
        """Delete an event by ID."""
        event = self.get_event_by_id(event_id)
        return self.event_dao.delete_event(event)

    def add_genre_to_event(self, event_id, genre_id):
        """Associate a genre with an event."""
        try:
            e_id = int(event_id)
            g_id = int(genre_id)
        except (ValueError, TypeError):
            raise ValueError("event_id and genre_id must be valid integers.")

        # Ensure event exists
        self.get_event_by_id(e_id)
        self.event_dao.add_genre_to_event(e_id, g_id)
        return True

    def get_trending_event_this_week(self):
        """Retrieve the trending event for the current week."""
        return self.event_dao.get_trending_event_this_week()
