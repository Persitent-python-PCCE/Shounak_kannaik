"""
Authentication and User Service.

Handles business logic for user registration, authentication, and session management.
Receives DAOs via constructor injection to facilitate unit testing with mock DAOs.
"""
import jwt
import re
from datetime import datetime, timezone, timedelta
from flask import current_app
from common.exceptions import AuthenticationError
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

PHONE_REGEX = r"^\+?[0-9]{7,15}$"


class AuthService:
    """
    Service layer handling authentication logic.
    """

    def __init__(self, user_dao):
        """
        Constructor injection of the UserDAO dependency.

        :param user_dao: UserDAO instance (or fake/mock DAO in tests)
        """
        self.user_dao = user_dao
    
    def generate_token(self, user):
        secret_key = current_app.config.get("JWT_SECRET_KEY")
        expiry_hours = current_app.config.get("JWT_EXPIRY_HOURS")
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user.id,
            "role": user.role,
            "iat": now,
            "exp": now+timedelta(hours=expiry_hours)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
        

    def verify_token(self, token: str):
        try:
            secret_key = current_app.config.get("JWT_SECRET_KEY")
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired. Please login again")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token.")

    def register(self, data):
        if not data.get("username") or not data.get("password") or not data.get("email"):
            raise ValueError("Username, password, and email are required fields.")
        if self.user_dao.get_by_username(data["username"]):
            raise ValueError("Username already exists.")
        if self.user_dao.get_by_email(data["email"]):
            raise ValueError("Email already exists.")

        phone_no = data.get("phone_no")
        if phone_no and str(phone_no).strip():
            phone_no = str(phone_no).strip()
            if not re.match(PHONE_REGEX, phone_no):
                raise ValueError("Invalid phone number format. Must contain 7-15 digits with optional '+' prefix.")
        else:
            phone_no = None

        hashed_password = generate_password_hash(data["password"])
        user = User(
            username=data.get("username").strip() if isinstance(data.get("username"), str) else data.get("username"),
            password_hash=hashed_password,
            email=data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email"),
            phone_no=phone_no,
        )
        return self.user_dao.create_user(user)

    def login(self, data):
        if not data.get("username") or not data.get("password"):
            raise ValueError("Username and password are required fields.")
        user = self.user_dao.get_by_username(data["username"])
        if not user or not check_password_hash(user.password_hash, data["password"]):
            raise AuthenticationError("Invalid username or password.")
        if not user.is_active:
            raise AuthenticationError("User is inactive. Please contact support.")
        return user

    
