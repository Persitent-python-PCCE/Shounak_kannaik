from flask import jsonify
from werkzeug.exceptions import HTTPException
from common.exceptions import (
    AuthenticationError, AuthorizationError, ResourceNotFoundError, SeatUnavailableError, DuplicateBookingError
)

def register_error_handlers(app):
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        return jsonify(
            {
                "error": "Unauthorized",
                "message": error.message,
                "status": error.status_code
            }
        ), 401

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        return jsonify(
            {
                "error": "Forbiden",
                "message": error.message,
                "status": error.status_code
            }
        ), 403

    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found_error(error):
        return jsonify({
            "error": "not found",
            "message": error.message,
            "status": error.status_code
        }), 404

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify({
            "error": "bad request",
            "message": str(error),
            "status": 400
        }), 400

    @app.errorhandler(DuplicateBookingError)
    @app.errorhandler(SeatUnavailableError)
    def handle_seat_unavailable_error(error):
        return jsonify({
            "error": "Conflict",
            "message": str(error),
            "status": 409
        }), 409

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            "error": error.name,
            "message": error.description,
            "status": error.code
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception(f"unhandled exception: {error}")
        return jsonify({
            "error": "internal server error",
            "message": "an unexpected error occured",
            "status": 500
        }), 500
        