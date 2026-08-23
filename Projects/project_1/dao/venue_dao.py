"""
Venue Data Access Object (DAO).

This class is the ONLY place allowed to execute database queries (db.session,
Model.query, etc.) related to Venue entities.
"""

from models.venue import Venue
from config.database import db


class VenueDAO:
    """
    DAO handling database interactions for Venue records.
    Holds no constructor arguments and interacts directly with the global db instance.
    """
    def get_all_venues(self):
        return Venue.query.all()

    def get_by_id(self, venue_id):
        return db.session.get(Venue, venue_id)

    def create_venue(self, venue):
        db.session.add(venue)
        db.session.commit()
        return venue
    
    def update_venue(self, venue):
        db.session.commit()
        return venue
    
    def delete_venue(self, venue):
        db.session.delete(venue)
        db.session.commit()
        return True

    def get_by_name(self, name):
        return Venue.query.filter_by(name=name).first()
    
    def filter_venue(self, filters: dict):
        query = db.select(Venue)

        if filters.get("name"):
            name_filter = filters["name"]
            query = query.where(Venue.name.ilike(f"%{name_filter}%"))
        if filters.get("city"):
            query = query.where(Venue.city.ilike(filters["city"]))
        if filters.get("state"):
            query = query.where(Venue.state.ilike(filters["state"]))
        if filters.get("country"):
            query = query.where(Venue.country.ilike(filters["country"]))
        if filters.get("min_capacity"):
            query = query.where(Venue.capacity >= filters["min_capacity"])
        if filters.get("max_capacity"):
            query = query.where(Venue.capacity <= filters["max_capacity"])
        
        return db.session.execute(query).scalars().all()
    
    def get_venue_by_name(self, name):
        venues = db.session.execute(
            db.select(Venue).where(Venue.name.ilike(f"%{name}%"))
        ).scalars().all()
        return venues

    def create_sections_and_seats(self, venue_id, sections_data):
        """
        Creates sections and programmatically generates seats for a venue.
        sections_data: list of dicts with keys 'name', 'price', 'row_count', 'seats_per_row'.
        """
        from models.venue import Section, Seat

        for sec_data in sections_data:
            section_name = sec_data.get("name") or "Main"
            price = float(sec_data.get("price") or 0.00)
            row_count = int(sec_data.get("row_count", 0))
            seats_per_row = int(sec_data.get("seats_per_row", 0))

            if row_count <= 0 or seats_per_row <= 0:
                continue

            section = Section(
                venue_id=venue_id,
                name=section_name,
                price=price
            )
            db.session.add(section)
            db.session.flush()

            for r_idx in range(row_count):
                row_name = self._generate_row_name(r_idx)
                for s_num in range(1, seats_per_row + 1):
                    seat_number = f"{row_name}{s_num}"
                    seat = Seat(
                        section_id=section.id,
                        row=row_name,
                        number=seat_number,
                        seat_type="Regular"
                    )
                    db.session.add(seat)

        db.session.commit()

    def _generate_row_name(self, index):
        """Convert 0 -> 'A', 1 -> 'B', ..., 25 -> 'Z', 26 -> 'AA'."""
        result = ""
        index += 1
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            result = chr(65 + remainder) + result
        return result