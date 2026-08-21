"""
Pytest configuration and fixture definitions.
"""

import pytest
from app import create_app
from config.settings import TestingConfig
from config.database import db
from config.settings import TestingConfig
from config.database import db
from models.user import User
from common.roles import Role
from service.auth_service import AuthService
from dao.user_dao import UserDAO
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app_instance = create_app(TestingConfig)

    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for making HTTP requests."""
    return app.test_client()

@pytest.fixture
def auth_service():
    return AuthService(UserDAO())

@pytest.fixture
def customer_user(app):
    """Create a test customer user."""
    user = User(
        username="john_customer",
        email="customer@example.com",
        password_hash=generate_password_hash("Password123!"),
        role=Role.CUSTOMER,
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user
    
@pytest.fixture
def admin_user(app):
    """Create a test admin user."""
    user = User(
        username="sarah_admin",
        email="admin@example.com",
        password_hash=generate_password_hash("AdminPass123!"),
        role=Role.ADMIN,
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def customer_headers(app, auth_service, customer_user):
    """Authorization headers for a customer."""
    token = auth_service.generate_token(customer_user)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(app, auth_service, admin_user):
    """Authorization headers for an admin."""
    token = auth_service.generate_token(admin_user)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def runner(app):
    """A test CLI runner for testing Flask CLI commands."""
    return app.test_cli_runner()
