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

    def create_booking_with_items(self, user_id, schedule_id, seat_ids, payment_mode_id):
        try:
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
                        BookingStatus.status_name != "cancelled"
                    ),
                    db.or_(
                        PaymentStatus.status_name == "completed",
                        db.and_(
                            PaymentStatus.status_name == "pending",
                            Booking.created_at >= five_min_check
                        )
                    )
                ).first()
            )
            if active_conflict:
                raise SeatUnavailableError("One or more selected seats are already reserved or booked")
            reserved_status = self.get_booking_status_by_name("reserved")
            pending_payment = (
                db.session.execute(db.select(PaymentStatus).where(PaymentStatus.status_name == "pending"))
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