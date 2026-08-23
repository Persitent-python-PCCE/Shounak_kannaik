from flask import jsonify, request, render_template, redirect, url_for
from werkzeug.exceptions import HTTPException
from common.exceptions import (
    AuthenticationError, AuthorizationError, ResourceNotFoundError, SeatUnavailableError, DuplicateBookingError
)


def wants_json_response():
    """Determine whether the client expects JSON or an HTML web page."""
    if request.path.startswith("/ui"):
        return False
    api_prefixes = ("/auth", "/events", "/venue", "/bookings", "/admin", "/payments", "/documents", "/schedules", "/api")
    if any(request.path.startswith(prefix) for prefix in api_prefixes):
        return True
    if request.accept_mimetypes.best_match(["application/json", "text/html"]) == "application/json":
        return True
    if request.accept_mimetypes.accept_html:
        return False
    return True


def register_error_handlers(app):
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        if not wants_json_response():
            return redirect(url_for("auth_web.login"))
        return jsonify(
            {
                "error": "Unauthorized",
                "message": error.message,
                "status": error.status_code
            }
        ), 401

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        if not wants_json_response():
            return render_template("403.html"), 403
        return jsonify(
            {
                "error": "Forbiden",
                "message": error.message,
                "status": error.status_code
            }
        ), 403

    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found_error(error):
        if not wants_json_response():
            return render_template("404.html"), 404
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

    @app.errorhandler(404)
    def handle_404(error):
        if not wants_json_response():
            return render_template("404.html"), 404
        return jsonify({
            "error": "Not Found",
            "message": getattr(error, "description", "The requested URL was not found on the server."),
            "status": 404
        }), 404

    @app.errorhandler(403)
    def handle_403(error):
        if not wants_json_response():
            return render_template("403.html"), 403
        return jsonify({
            "error": "Forbidden",
            "message": getattr(error, "description", "You do not have permission to access this resource."),
            "status": 403
        }), 403

    @app.errorhandler(500)
    def handle_500(error):
        if not wants_json_response():
            return render_template("500.html"), 500
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "status": 500
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        if error.code == 404 and not wants_json_response():
            return render_template("404.html"), 404
        if error.code == 403 and not wants_json_response():
            return render_template("403.html"), 403
        if error.code == 500 and not wants_json_response():
            return render_template("500.html"), 500
        return jsonify({
            "error": error.name,
            "message": error.description,
            "status": error.code
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception(f"unhandled exception: {error}")
        if not wants_json_response():
            return render_template("500.html"), 500
        return jsonify({
            "error": "internal server error",
            "message": "an unexpected error occured",
            "status": 500
        }), 500
        