"""
Booking Service.

Handles business logic for seat reservation, ticket pricing, booking retrieval, and cancellation.
Receives BookingDAO via constructor injection to facilitate unit testing with mock DAOs.
"""
from datetime import datetime, timedelta, timezone
from dao.payment_dao import PaymentDAO
from common.exceptions import AuthorizationError


class BookingService:
    """
    Service layer handling booking and reservation workflows.
    """

    def __init__(self, booking_dao, payment_dao=None):
        """
        Constructor injection of the BookingDAO and PaymentDAO dependencies.

        :param booking_dao: BookingDAO instance (or fake/mock DAO in tests)
        :param payment_dao: PaymentDAO instance (or fake/mock DAO in tests)
        """
        self.booking_dao = booking_dao
        self.payment_dao = payment_dao or PaymentDAO()

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

    def cancel_booking(self, booking_id, user_id=None, role=None):
        """
        Cancel a booking by setting its status to 'cancelled' and payment status to 'refunded'.
        Enforces ownership/admin authorization and 1-hour cancellation window before event start.
        """
        booking = self.get_booking_by_id(booking_id)

        if user_id is not None and booking.user_id != user_id and role != "admin":
            raise AuthorizationError("Unauthorized to cancel this booking")
        if booking.booking_status and booking.booking_status.status_name.lower() == "cancelled":
            raise ValueError("Booking is already cancelled.")
        if not booking.schedule or not booking.schedule.start_datetime:
            raise ValueError("Associated schedule start time not found for this booking.")

        start_datetime = booking.schedule.start_datetime
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if (start_datetime - now) <= timedelta(hours=1):
            raise ValueError("Cancellations are not permitted within 1 hour of the scheduled time.")

        cancelled_status = self.booking_dao.get_booking_status_by_name("cancelled")
        refunded_status = self.payment_dao.get_payment_status_by_name("refunded")
        
        booking.booking_status_id = cancelled_status.id
        booking.payment_status_id = refunded_status.id

        return self.booking_dao.update_booking(booking)

    def create_booking(self, user_id, schedule_id, seat_ids, payment_mode_id):
        unique_seats = sorted(list(set(seat_ids)))
        if not unique_seats:
            raise ValueError("At least one valid seat must be selected")
        return self.booking_dao.create_booking_with_items(
            user_id=user_id,
            schedule_id=schedule_id,
            seat_ids=unique_seats,
            payment_mode_id=payment_mode_id
        )
        
