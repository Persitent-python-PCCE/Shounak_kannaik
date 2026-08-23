"""
Payment Data Access Object (DAO).

This class is the ONLY place allowed to execute database queries (db.session,
Model.query, etc.) related to Payment entities.
"""

from models.payment import PaymentMode, PaymentStatus
from config.database import db


class PaymentDAO:
    """
    DAO handling database interactions for PaymentMode and PaymentStatus records.
    Holds no constructor arguments and interacts directly with the global db instance.
    """

    def get_all_payment_modes(self):
        """Fetch all payment modes."""
        return db.session.execute(db.select(PaymentMode)).scalars().all()

    def get_payment_mode_by_id(self, mode_id):
        """Fetch a payment mode by primary key ID."""
        return db.session.get(PaymentMode, mode_id)

    def get_all_payment_statuses(self):
        """Fetch all payment statuses."""
        return db.session.execute(db.select(PaymentStatus)).scalars().all()

    def get_payment_status_by_id(self, status_id):
        """Fetch a payment status by primary key ID."""
        return db.session.get(PaymentStatus, status_id)

    def get_payment_status_by_name(self, status_name):
        """Fetch a payment status by its unique status name (case-insensitive)."""
        if not status_name:
            return None
        status = db.session.execute(
            db.select(PaymentStatus).where(db.func.lower(PaymentStatus.status_name) == status_name.lower())
        ).scalar_one_or_none()
        if not status and status_name.lower() in ["pending", "completed", "refunded", "expired", "failed"]:
            status = PaymentStatus(status_name=status_name.lower())
            db.session.add(status)
            db.session.commit()
        return status

    def create_transaction(self, transaction):
        """Persist a new PaymentTransaction record."""
        db.session.add(transaction)
        db.session.commit()
        return transaction
