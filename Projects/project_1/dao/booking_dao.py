"""
Booking Data Access Object (DAO).

This class is the ONLY place allowed to execute database queries (db.session,
Model.query, etc.) related to Booking entities.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import joinedload
from models.venue import Seat
from models.payment import PaymentStatus
from models.booking import Booking, BookingItem, BookingStatus
from common.exceptions import SeatUnavailableError
from config.database import db


class BookingDAO:
    """
    DAO handling database interactions for Booking, BookingItem, and BookingStatus records.
    Holds no constructor arguments and interacts directly with the global db instance.
    """

    def expire_stale_bookings(self):
        """
        Lazily expire all pending/unpaid bookings older than 5 minutes.
        Updates booking_status to 'cancelled' and payment_status to 'expired'.
        """
        try:
            cancelled_status = self.get_booking_status_by_name("cancelled")
            expired_payment_status = db.session.execute(
                db.select(PaymentStatus).where(db.func.lower(PaymentStatus.status_name) == "expired")
            ).scalar_one_or_none()

            if not expired_payment_status:
                expired_payment_status = PaymentStatus(status_name="expired")
                db.session.add(expired_payment_status)
                db.session.flush()

            stale_candidates = (
                db.session.query(Booking)
                .join(PaymentStatus, Booking.payment_status_id == PaymentStatus.id)
                .outerjoin(BookingStatus, Booking.booking_status_id == BookingStatus.id)
                .filter(
                    db.func.lower(PaymentStatus.status_name) == "pending",
                    db.or_(
                        Booking.booking_status_id == None,
                        db.and_(
                            db.func.lower(BookingStatus.status_name) != "cancelled",
                            db.func.lower(BookingStatus.status_name) != "confirmed"
                        )
                    )
                ).all()
            )

            modified = False
            now_utc = datetime.now(timezone.utc)

            for b in stale_candidates:
                if not b.created_at:
                    continue

                if b.created_at.tzinfo is not None:
                    diff_seconds = (now_utc - b.created_at).total_seconds()
                else:
                    diff_seconds = (now_utc.replace(tzinfo=None) - b.created_at).total_seconds()

                if diff_seconds > 300:
                    if cancelled_status:
                        b.booking_status_id = cancelled_status.id
                    if expired_payment_status:
                        b.payment_status_id = expired_payment_status.id
                    modified = True

            if modified:
                db.session.commit()
        except Exception:
            db.session.rollback()

    def get_all_bookings(self):
        """Fetch all bookings from the database after expiring stale reservations."""
        self.expire_stale_bookings()
        return db.session.execute(db.select(Booking).order_by(Booking.created_at.desc())).scalars().all()

    def get_by_id(self, booking_id):
        """Fetch a booking by primary key ID after expiring stale reservations."""
        self.expire_stale_bookings()
        return db.session.get(Booking, booking_id)

    def get_bookings_for_user(self, user_id):
        """Fetch all bookings associated with a specific user after expiring stale reservations."""
        self.expire_stale_bookings()
        return db.session.execute(
            db.select(Booking).where(Booking.user_id == user_id).order_by(Booking.created_at.desc())
        ).scalars().all()

    def get_all_booking_statuses(self):
        """Fetch all booking status records."""
        return db.session.execute(db.select(BookingStatus)).scalars().all()

    def get_booking_status_by_name(self, status_name):
        """Fetch a booking status by its unique status name (case-insensitive)."""
        if not status_name:
            return None
        status = db.session.execute(
            db.select(BookingStatus).where(db.func.lower(BookingStatus.status_name) == status_name.lower())
        ).scalar_one_or_none()
        if not status and status_name.lower() in ["reserved", "confirmed", "cancelled", "pending"]:
            status = BookingStatus(status_name=status_name.lower())
            db.session.add(status)
            db.session.commit()
        return status

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

    def create_booking_with_items(self, user_id, schedule_id, seat_ids, payment_mode_id):
        try:
            self.expire_stale_bookings()
            seats = (db.session.query(Seat)
            .options(joinedload(Seat.section))
            .filter(Seat.id.in_(seat_ids))
            .with_for_update()
            .all())

            if(len(seats)!=len(set(seat_ids))):
                raise ValueError("One or more seats are invalid")
            
            five_min_check = datetime.now(timezone.utc) - timedelta(minutes=5)

            active_conflict = (
                db.session.query(BookingItem)
                .join(Booking, BookingItem.booking_id == Booking.id)
                .join(PaymentStatus, Booking.payment_status_id == PaymentStatus.id)
                .outerjoin(BookingStatus, Booking.booking_status_id == BookingStatus.id)
                .filter(
                    Booking.schedule_id == schedule_id,
                    BookingItem.seat_id.in_(seat_ids),
                    db.or_(
                        Booking.booking_status_id == None,
                        db.func.lower(BookingStatus.status_name) != "cancelled"
                    ),
                    db.or_(
                        db.func.lower(PaymentStatus.status_name) == "completed",
                        db.and_(
                            db.func.lower(PaymentStatus.status_name) == "pending",
                            Booking.created_at >= five_min_check
                        )
                    )
                ).first()
            )
            if active_conflict:
                raise SeatUnavailableError("One or more selected seats are already reserved or booked")
            reserved_status = self.get_booking_status_by_name("reserved")
            pending_payment = (
                db.session.execute(db.select(PaymentStatus).where(db.func.lower(PaymentStatus.status_name) == "pending"))
            ).scalar_one_or_none()
            total_amount = sum(float(seat.section.price) for seat in seats)
            booking = Booking(
                user_id = user_id,
                schedule_id = schedule_id,
                payment_mode_id = payment_mode_id,
                payment_status_id = pending_payment.id if pending_payment else None,
                booking_status_id = reserved_status.id if reserved_status else None,
                total_amount = total_amount
            )
            db.session.add(booking)
            db.session.flush()

            for seat in seats:
                item = BookingItem(
                    booking_id = booking.id,
                    seat_id = seat.id,
                    price = seat.section.price
                )
                db.session.add(item)

            db.session.commit()
            return booking 
            
        except Exception as e:
            db.session.rollback()
            raise e

    def get_booked_seat_ids(self, schedule_id):
        """Retrieve seat IDs that are currently active/reserved/booked for a schedule."""
        self.expire_stale_bookings()
        five_min_check = datetime.now(timezone.utc) - timedelta(minutes=5)
        results = (
            db.session.query(BookingItem.seat_id)
            .join(Booking, BookingItem.booking_id == Booking.id)
            .join(PaymentStatus, Booking.payment_status_id == PaymentStatus.id)
            .outerjoin(BookingStatus, Booking.booking_status_id == BookingStatus.id)
            .filter(
                Booking.schedule_id == schedule_id,
                db.or_(
                    Booking.booking_status_id == None,
                    db.func.lower(BookingStatus.status_name) != "cancelled"
                ),
                db.or_(
                    db.func.lower(PaymentStatus.status_name) == "completed",
                    db.and_(
                        db.func.lower(PaymentStatus.status_name) == "pending",
                        Booking.created_at >= five_min_check
                    )
                )
            ).all()
        )
        return {r[0] for r in results}