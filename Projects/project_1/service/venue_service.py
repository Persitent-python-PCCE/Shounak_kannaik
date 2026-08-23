from models.venue import Venue
from config.cache import cache


class VenueService:
    def __init__(self, venue_dao):
        self.venue_dao = venue_dao

    def __repr__(self):
        return "VenueService"

    def _invalidate_venue_caches(self):
        try:
            cache.delete_memoized(self.get_all_venues)
        except Exception:
            pass

    @cache.memoize(timeout=300)
    def get_all_venues(self):
        return self.venue_dao.get_all_venues()

    def get_by_id(self, id):
        return self.venue_dao.get_by_id(id)
    
    def get_venue_by_name(self, name):
        return self.venue_dao.get_venue_by_name(name)

    def create_venue(self, data):
        venue = Venue(
            name= data.get("name"),
            address = data.get("address"),
            city = data.get("city"),
            state = data.get("state"),
            country = data.get("country"),
            capacity = data.get("capacity")
        )
        created_venue = self.venue_dao.create_venue(venue)
        self._invalidate_venue_caches()
        return created_venue

    def update_venue(self, data):
        venue_id = data.get("venue_id")
        venue = self.get_by_id(venue_id)
        if not venue:
            raise ValueError("Venue not found.")
        if "name" in data and data["name"]:
            venue.name = data["name"]
        if "address" in data and data["address"]:
            venue.address = data["address"]
        if "city" in data and data["city"]:
            venue.city = data["city"]
        if "state" in data and data["state"]:
            venue.state = data["state"]
        if "country" in data and data["country"]:
            venue.country = data["country"]
        if "capacity" in data and data["capacity"]:
            venue.capacity = data["capacity"]
        
        updated_venue = self.venue_dao.update_venue(venue)
        self._invalidate_venue_caches()
        return updated_venue
    
    def delete_venue(self, venue_id):
        venue = self.get_by_id(venue_id)
        if not venue:
            raise ValueError("Venue not found.")
        deleted = self.venue_dao.delete_venue(venue)
        self._invalidate_venue_caches()
        return deleted
    
    def filter_venue(self, filters: dict):
        cleaned_filters= {}
        if  filters.get("name"):
            cleaned_filters["name"] = filters.get("name").strip()
        if filters.get("city"):
            cleaned_filters["city"] = filters.get("city").strip()
        if filters.get("state"):
            cleaned_filters["state"] = filters.get("state").strip()
        if filters.get("country"):
            cleaned_filters["country"] = filters.get("country").strip()
        if filters.get("min_capacity"):
            try:
                cleaned_filters["min_capacity"] = int(filters.get("min_capacity").strip())
            except ValueError:
                raise ValueError("Minimun Capacity must be a valid numeric value")
        if filters.get("max_capacity"):
            try:
                cleaned_filters["max_capacity"] = int(filters.get("max_capacity").strip())
            except ValueError:
                raise ValueError("Maximun Capacity must be a valid numeric value")        
        return self.venue_dao.filter_venue(cleaned_filters)

    def create_venue_with_layout(self, venue_data, sections_data=None):
        """Create venue and its sections and seats."""
        total_seats = 0
        if sections_data:
            for s in sections_data:
                try:
                    r_cnt = int(s.get("row_count") or 0)
                    s_cnt = int(s.get("seats_per_row") or 0)
                    total_seats += r_cnt * s_cnt
                except (ValueError, TypeError):
                    pass

        if total_seats > 0:
            entered_cap = venue_data.get("capacity") or 0
            venue_data["capacity"] = max(entered_cap, total_seats)

        venue = self.create_venue(venue_data)

        if sections_data and hasattr(self.venue_dao, "create_sections_and_seats"):
            self.venue_dao.create_sections_and_seats(venue.id, sections_data)

        return venue
        