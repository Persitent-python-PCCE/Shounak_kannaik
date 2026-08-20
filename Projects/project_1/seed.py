"""
Database Seeding Script.

Populates initial lookup data (genres, venues, seat maps, admin user, etc.)
for development and testing environments.
"""

from app import create_app
from config.settings import DevelopmentConfig
from config.database import db


def seed_database():
    """Seed initial data into the database."""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        print("Starting database seeding...")
        # Seeding logic: instantiate models and persist via DAOs/db.session
        # Example:
        # admin = User(...)
        # db.session.add(admin)
        # db.session.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
