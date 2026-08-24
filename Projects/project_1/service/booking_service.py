from datetime import datetime, timedelta, timezone
from dao.payment_dao import PaymentDAO
from common.exceptions import AuthorizationError


class BookingService:

    def __init__(self, booking_dao, payment_dao=None):
        self.booking_dao = booking_dao
        self.payment_dao = payment_dao or PaymentDAO()

    def get_booking_by_id(self, booking_id):
        booking = self.booking_dao.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found.")
        return booking

    def get_bookings_for_user(self, user_id):
        return self.booking_dao.get_bookings_for_user(user_id)

    def get_all_bookings(self):
        return self.booking_dao.get_all_bookings()

    def cancel_booking(self, booking_id, user_id=None, role=None):
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

    def get_booked_seat_ids(self, schedule_id):
        if hasattr(self.booking_dao, "get_booked_seat_ids"):
            return self.booking_dao.get_booked_seat_ids(schedule_id)
        return set()

    def confirm_payment(self, booking_id, payment_mode_id=None, gateway_transaction_id=None):
        import uuid
        from models.payment import PaymentTransaction

        booking = self.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found.")


        is_cancelled = booking.booking_status and booking.booking_status.status_name.lower() == "cancelled"
        is_expired = booking.payment_status and booking.payment_status.status_name.lower() == "expired"
        if is_cancelled or is_expired:
            raise ValueError("This booking reservation has expired (5-minute payment window elapsed). Please select your seats again.")


        if booking.created_at:
            now_utc = datetime.now(timezone.utc)
            if booking.created_at.tzinfo is not None:
                diff_seconds = (now_utc - booking.created_at).total_seconds()
            else:
                diff_seconds = (now_utc.replace(tzinfo=None) - booking.created_at).total_seconds()

            if diff_seconds > 300 and (not booking.payment_status or booking.payment_status.status_name.lower() != "completed"):
                cancelled_status = self.booking_dao.get_booking_status_by_name("cancelled")
                expired_status = self.payment_dao.get_payment_status_by_name("expired")
                if cancelled_status:
                    booking.booking_status_id = cancelled_status.id
                if expired_status:
                    booking.payment_status_id = expired_status.id
                self.booking_dao.update_booking(booking)
                raise ValueError("This booking reservation has expired (5-minute payment window elapsed). Please select your seats again.")

        if payment_mode_id:
            booking.payment_mode_id = int(payment_mode_id)

        completed_status = self.payment_dao.get_payment_status_by_name("completed")
        confirmed_status = self.booking_dao.get_booking_status_by_name("confirmed")

        if completed_status:
            booking.payment_status_id = completed_status.id
        if confirmed_status:
            booking.booking_status_id = confirmed_status.id

        txn = PaymentTransaction(
            booking_id=booking.id,
            amount=booking.total_amount or 0.00,
            gateway_transaction_id=gateway_transaction_id or f"TXN-{uuid.uuid4().hex[:10].upper()}",
            status="Completed",
            paid_at=datetime.now(timezone.utc)
        )
        if hasattr(self.payment_dao, "create_transaction"):
            self.payment_dao.create_transaction(txn)

        return self.booking_dao.update_booking(booking)
