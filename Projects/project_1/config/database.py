"""
Database and extensions configuration.

This module initializes the SQLAlchemy, Migrate, and LoginManager instances
without binding them to a specific Flask app instance. They are bound during
application factory execution via db.init_app(app).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Instantiate extensions (unbound to any specific app instance)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
