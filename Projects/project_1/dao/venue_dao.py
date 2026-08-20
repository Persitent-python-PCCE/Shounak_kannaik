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