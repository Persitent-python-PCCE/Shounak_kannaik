
from flask_login import UserMixin
from config.database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_no = db.Column(db.String(20), unique=True, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now())
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default="customer")
    last_active = db.Column(db.DateTime(timezone=True))


    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    documents = db.relationship("UserDocument", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone_no": self.phone_no,
            "role": self.role,
            "is_active": self.is_active,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
