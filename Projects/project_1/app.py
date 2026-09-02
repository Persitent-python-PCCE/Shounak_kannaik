
from flask import Flask, redirect, url_for
from flask_cors import CORS
from config.settings import DevelopmentConfig
from config.database import db, migrate, login_manager
from config.cache import cache
from dao.user_dao import UserDAO
import models                                                              

from middleware.error_handlers import register_error_handlers
from middleware.logging_middleware import register_global_middleware


from controller.auth_controller import auth_controller
from controller.event_controller import event_controller
from controller.venue_controller import venue_controller
from controller.booking_controller import booking_controller
from controller.admin_controller import admin_controller
from controller.api_controller import api_controller
from controller.payment_controller import payment_controller
from controller.document_controller import document_controller
from controller.schedule_controller import schedule_controller


from controller.web.auth_web_controller import auth_web
from controller.web.events_web_controller import events_web
from controller.web.bookings_web_controller import bookings_web
from controller.web.payments_web_controller import payments_web
from controller.web.documents_web_controller import documents_web
from controller.web.admin_web_controller import admin_web
from service.auth_service import AuthService


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth_controller.login"
    cache.init_app(app)

    register_error_handlers(app)
    register_global_middleware(app)

    @login_manager.user_loader
    def load_user(user_id):
        return UserDAO().get_by_id(int(user_id))


    @app.context_processor
    def inject_current_user():
        from flask import request, g
        token = request.cookies.get("access_token_cookie")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if token:
            try:
                auth_svc = AuthService(UserDAO())
                payload = auth_svc.verify_token(token)
                uid = payload.get("user_id")
                user = UserDAO().get_by_id(uid)
                if user:
                    return {
                        "current_user": {
                            "id": user.id,
                            "user_id": user.id,
                            "username": user.username,
                            "role": user.role,
                            "email": user.email
                        }
                    }
                elif payload.get("role"):
                    return {
                        "current_user": {
                            "id": uid,
                            "user_id": uid,
                            "username": "User",
                            "role": payload.get("role"),
                            "email": ""
                        }
                    }
            except Exception:
                pass
        return {"current_user": None}


    app.register_blueprint(auth_controller, url_prefix="/auth")
    app.register_blueprint(event_controller, url_prefix="/events")
    app.register_blueprint(venue_controller, url_prefix="/venue")
    app.register_blueprint(booking_controller, url_prefix="/bookings")
    app.register_blueprint(admin_controller, url_prefix="/admin")
    app.register_blueprint(api_controller, url_prefix="/api")
    app.register_blueprint(payment_controller, url_prefix="/payments")
    app.register_blueprint(document_controller, url_prefix="/documents")
    app.register_blueprint(schedule_controller, url_prefix="/schedules")


    app.register_blueprint(auth_web, url_prefix="/ui")
    app.register_blueprint(events_web, url_prefix="/ui")
    app.register_blueprint(bookings_web, url_prefix="/ui")
    app.register_blueprint(payments_web, url_prefix="/ui")
    app.register_blueprint(documents_web, url_prefix="/ui")
    app.register_blueprint(admin_web, url_prefix="/ui/admin")


    @app.route("/")
    def index():
        return redirect(url_for("events_web.list_events"))

    @app.route("/health")
    def health():
        return {"status": "healthy"}, 200

    return app


if __name__ == "__main__":
    app = create_app(DevelopmentConfig)
    app.run(host="0.0.0.0", port=5000, debug=True)
