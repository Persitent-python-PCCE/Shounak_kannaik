"""
Pytest configuration and fixture definitions.
"""

import pytest
from app import create_app
from config.settings import TestingConfig
from config.database import db


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
def runner(app):
    """A test CLI runner for testing Flask CLI commands."""
    return app.test_cli_runner()
