"""
Authentication and User Service.

Handles business logic for user registration, authentication, and session management.
Receives DAOs via constructor injection to facilitate unit testing with mock DAOs.
"""

from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash


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

    def register(self, data):
        if not data.get("username") or not data.get("password") or not data.get("email"):
            raise ValueError("Username, password, and email are required fields.")
        if self.user_dao.get_by_username(data["username"]):
            raise ValueError("Username already exists.")
        if self.user_dao.get_by_email(data["email"]):
            raise ValueError("Email already exists.")

        hashed_password = generate_password_hash(data["password"])
        user = User(
            username=data.get("username"),
            password_hash=hashed_password,
            email=data.get("email"),
            phone_no=data.get("phone_no"),
        )
        return self.user_dao.create_user(user)

    def login(self, data):
        if not data.get("username") or not data.get("password"):
            raise ValueError("Username and password are required fields.")
        user = self.user_dao.get_by_username(data["username"])
        if not user or not check_password_hash(user.password_hash, data["password"]):
            raise ValueError("Invalid username or password.")
        if not user.is_active:
            raise ValueError("User is inactive. Please contact support.")
        return user
    
