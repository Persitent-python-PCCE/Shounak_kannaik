"""
Booking Data Access Object (DAO).

This class is the ONLY place allowed to execute database queries (db.session,
Model.query, etc.) related to Booking entities.
"""

from models.booking import Booking, BookingItem, BookingStatus
from config.database import db


class BookingDAO:
    """
    DAO handling database interactions for Booking, BookingItem, and BookingStatus records.
    Holds no constructor arguments and interacts directly with the global db instance.
    """

    def get_all_bookings(self):
        """Fetch all bookings from the database."""
        return db.session.execute(db.select(Booking)).scalars().all()

    def get_by_id(self, booking_id):
        """Fetch a booking by primary key ID."""
        return db.session.get(Booking, booking_id)

    def get_bookings_for_user(self, user_id):
        """Fetch all bookings associated with a specific user."""
        return db.session.execute(
            db.select(Booking).where(Booking.user_id == user_id)
        ).scalars().all()

    def get_all_booking_statuses(self):
        """Fetch all booking status records."""
        return db.session.execute(db.select(BookingStatus)).scalars().all()

    def get_booking_status_by_name(self, status_name):
        """Fetch a booking status by its unique status name."""
        return db.session.execute(
            db.select(BookingStatus).where(BookingStatus.status_name == status_name)
        ).scalar_one_or_none()

    def create_booking(self, booking):
        """Persist a new Booking record."""
        db.session.add(booking)
        db.session.commit()
        return booking

    def update_booking(self, booking):
        """Commit modifications made to a Booking record."""
        db.session.commit()
        return booking

    def delete_booking(self, booking):
        """Delete a Booking record from the database."""
        db.session.delete(booking)
        db.session.commit()
        return True

    def create_booking_with_items(self, booking, items):
        # TODO: implement manually — requires SELECT FOR UPDATE row locking
        # on seats, atomic commit of Booking + BookingItem rows, and rollback
        # on any seat conflict. Not auto-generated on purpose.
        raise NotImplementedError
