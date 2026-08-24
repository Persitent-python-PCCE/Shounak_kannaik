
from models.event import Event
from config.cache import cache


class EventService:

    def __init__(self, event_dao):
        self.event_dao = event_dao

    def __repr__(self):
        return "EventService"

    def _invalidate_event_caches(self):
        try:
            cache.delete_memoized(self.get_all_events)
            cache.delete_memoized(self.get_all_event_types)
            cache.delete_memoized(self.get_all_genres)
            cache.delete_memoized(self.get_trending_event_this_week)
        except Exception:
            pass

    @cache.memoize(timeout=300)
    def get_all_events(self):
        return self.event_dao.get_all_events()

    def get_all_events_paginated(self, page=1, per_page=10):
        try:
            page = int(page)
            per_page = int(per_page)
        except (ValueError, TypeError):
            page, per_page = 1, 10
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        return self.event_dao.get_all_events(page=page, per_page=per_page)

    def get_event_by_id(self, event_id):
        event = self.event_dao.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found.")
        return event

    def filter_events(self, filters: dict, page=None, per_page=None):
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

        if page is not None and per_page is not None:
            try:
                p = int(page)
                pp = int(per_page)
            except (ValueError, TypeError):
                p, pp = 1, 10
            if p < 1:
                p = 1
            if pp < 1:
                pp = 10
            return self.event_dao.filter_events(cleaned_filters, page=p, per_page=pp)

        return self.event_dao.filter_events(cleaned_filters)

    @cache.memoize(timeout=300)
    def get_all_event_types(self):
        return self.event_dao.get_all_event_types()

    @cache.memoize(timeout=300)
    def get_all_genres(self):
        return self.event_dao.get_all_genres()

    def get_genres_for_event(self, event_id):
        return self.event_dao.get_genres_for_event(event_id)

    def create_event(self, data):
        if not data.get("name"):
            raise ValueError("Event name is required.")

        event = Event(
            name=data.get("name").strip(),
            about=data.get("about"),
            event_type_id=data.get("event_type_id"),
            age_rating=data.get("age_rating"),
            poster_image_path=data.get("poster_image_path"),
        )
        created_event = self.event_dao.create_event(event)
        self._invalidate_event_caches()
        return created_event

    def update_event(self, data):
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

        updated_event = self.event_dao.update_event(event)
        self._invalidate_event_caches()
        return updated_event

    def delete_event(self, event_id):
        event = self.get_event_by_id(event_id)
        deleted = self.event_dao.delete_event(event)
        self._invalidate_event_caches()
        return deleted

    def add_genre_to_event(self, event_id, genre_id):
        try:
            e_id = int(event_id)
            g_id = int(genre_id)
        except (ValueError, TypeError):
            raise ValueError("event_id and genre_id must be valid integers.")


        self.get_event_by_id(e_id)
        self.event_dao.add_genre_to_event(e_id, g_id)
        self._invalidate_event_caches()
        return True

    def set_genres_for_event(self, event_id, genre_ids):
        try:
            e_id = int(event_id)
        except (ValueError, TypeError):
            raise ValueError("event_id must be a valid integer.")

        self.get_event_by_id(e_id)
        valid_ids = []
        if genre_ids:
            for gid in genre_ids:
                try:
                    val = int(gid)
                    if val > 0:
                        valid_ids.append(val)
                except (ValueError, TypeError):
                    continue
        self.event_dao.set_genres_for_event(e_id, valid_ids)
        self._invalidate_event_caches()
        return True

    @cache.memoize(timeout=300)
    def get_trending_event_this_week(self):
        return self.event_dao.get_trending_event_this_week()
