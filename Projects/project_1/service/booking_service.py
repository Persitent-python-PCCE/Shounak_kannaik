"""
Booking Service.

Handles business logic for seat reservation, ticket pricing, booking retrieval, and cancellation.
Receives BookingDAO via constructor injection to facilitate unit testing with mock DAOs.
"""


class BookingService:
    """
    Service layer handling booking and reservation workflows.
    """

    def __init__(self, booking_dao):
        """
        Constructor injection of the BookingDAO dependency.

        :param booking_dao: BookingDAO instance (or fake/mock DAO in tests)
        """
        self.booking_dao = booking_dao

    def get_booking_by_id(self, booking_id):
        """Retrieve a booking by primary key ID."""
        booking = self.booking_dao.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found.")
        return booking

    def get_bookings_for_user(self, user_id):
        """Retrieve all bookings associated with a specific user."""
        return self.booking_dao.get_bookings_for_user(user_id)

    def get_all_bookings(self):
        """Retrieve all bookings across the system (admin access)."""
        return self.booking_dao.get_all_bookings()

    def cancel_booking(self, booking_id):
        """
        Cancel a booking by setting its status to 'Cancelled'.

        NOTE: This method ONLY updates the booking's status field.
        Seat availability in this system is determined by the presence of BookingItem rows
        linked to a booking — there is no is_available flag on the Seat model.
        Seat 'unlocking' on cancellation (if desired) must be handled in the manual
        create_booking_with_items flow, not here.
        PREREQUISITE: A BookingStatus record with status_name="Cancelled" must exist in the DB.
        """
        booking = self.get_booking_by_id(booking_id)
        cancelled_status = self.booking_dao.get_booking_status_by_name("Cancelled")
        if not cancelled_status:
            raise ValueError("Booking status 'Cancelled' not found. Ensure booking statuses are seeded.")

        booking.booking_status_id = cancelled_status.id
        return self.booking_dao.update_booking(booking)

    def create_booking(self, data):
        # TODO: implement manually — this is the seat-locking transaction
        # (SELECT FOR UPDATE, atomic Booking + BookingItem creation,
        # rollback on conflict). Being written by hand intentionally.
        raise NotImplementedError
