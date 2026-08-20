"""
Application Factory module.

Defines create_app() to instantiate, configure, and assemble the Flask application
with database connections, migration hooks, authentication managers, and blueprint routing.
"""

from controller.venue_controller import venue_controller
from flask import Flask
from config.settings import DevelopmentConfig
from config.database import db, migrate, login_manager
from dao.user_dao import UserDAO
import models  # Ensure all SQLAlchemy models are registered for migrations

# Import controllers
from controller.auth_controller import auth_controller
from controller.event_controller import event_controller
from controller.venue_controller import venue_controller
from controller.booking_controller import booking_controller
from controller.admin_controller import admin_controller
from controller.api_controller import api_controller


def create_app(config_class=DevelopmentConfig):
    """
    Application Factory function.

    :param config_class: Configuration class containing app settings
    :return: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the application instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth_controller.login"

    # Flask-Login user loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return UserDAO().get_by_id(int(user_id))

    # Register Blueprints with url prefixes
    app.register_blueprint(auth_controller, url_prefix="/auth")
    app.register_blueprint(event_controller, url_prefix="/events")
    app.register_blueprint(venue_controller, url_prefix = "/venue")
    app.register_blueprint(booking_controller, url_prefix="/bookings")
    app.register_blueprint(admin_controller, url_prefix="/admin")
    app.register_blueprint(api_controller, url_prefix="/api")

    # Root redirect / health route
    @app.route("/")
    def index():
        from flask import jsonify
        return jsonify({"message": "Ticket Booking API is running"}), 200

    return app


if __name__ == "__main__":
    app = create_app(DevelopmentConfig)
    app.run(debug=True)
