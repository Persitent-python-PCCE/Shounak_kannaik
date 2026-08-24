
from config.database import db


class PaymentMode(db.Model):
    __tablename__ = "payment_modes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mode_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    bookings = db.relationship("Booking", back_populates="payment_mode")

    def to_dict(self):
        return {
            "id": self.id,
            "mode_name": self.mode_name,
            "description": self.description,
        }


class PaymentStatus(db.Model):
    __tablename__ = "payment_statuses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(50), unique=True, nullable=False)

    bookings = db.relationship("Booking", back_populates="payment_status")

    def to_dict(self):
        return {
            "id": self.id,
            "status_name": self.status_name,
        }


class PaymentTransaction(db.Model):
    __tablename__ = "payment_transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    gateway_transaction_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Pending")
    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())


    booking = db.relationship("Booking", back_populates="transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "amount": float(self.amount) if self.amount is not None else 0.00,
            "gateway_transaction_id": self.gateway_transaction_id,
            "status": self.status,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
