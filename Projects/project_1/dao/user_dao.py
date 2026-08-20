"""
User Data Access Object (DAO).

This class is the ONLY place allowed to execute database queries (db.session,
Model.query, etc.) related to User entities.
"""

from models.user import User
from config.database import db


class UserDAO:
    """
    DAO handling database interactions for User records.
    Holds no constructor arguments and interacts directly with the global db instance.
    """

    def get_all_users(self):
        """Fetch all users from the database."""
        return db.session.query(User).all()

    def get_by_id(self, user_id):
        """Fetch a user by primary key ID."""
        return db.session.get(User, user_id)

    def create_user(self, user):
        """Persist a new User record."""
        db.session.add(user)
        db.session.commit()
        return user
    
    def get_by_username(self, username):
        user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()
        return user

    def get_by_email(self, email):
        return db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar_one_or_none()

    def update_user(self, user):
        db.session.commit()
        return user

    def delete_user(self, user):
        db.session.delete(user)
        db.session.commit()
        return True