"""
Admin Controller.
"""

from flask import Blueprint, request, jsonify
from service.admin_service import AdminService
from service.venue_service import VenueService
from service.event_service import EventService
from service.booking_service import BookingService
from service.schedule_service import ScheduleService
from dao.user_dao import UserDAO
from dao.venue_dao import VenueDAO
from dao.event_dao import EventDAO
from dao.booking_dao import BookingDAO
from dao.schedule_dao import ScheduleDAO
from common.decorators import authenticate, authorize
from common.roles import Role

admin_controller = Blueprint("admin_controller", __name__)
admin_service = AdminService(UserDAO())
venue_service = VenueService(VenueDAO())
event_service = EventService(EventDAO())
booking_service = BookingService(BookingDAO())
schedule_service = ScheduleService(ScheduleDAO())


# ==========================================
# User Management Routes (Admin Only)
# ==========================================

@admin_controller.route("/users", methods=["GET"])
@authenticate
@authorize(Role.ADMIN)
def get_users():
    """Endpoint to list all users."""
    try:
        users = admin_service.get_all_users()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
@authenticate
@authorize(Role.ADMIN)
def update_user(user_id):
    data = request.get_json() or {}
    data["user_id"] = user_id
    try:
        user = admin_service.update_user(data)
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/users/<int:user_id>", methods=["DELETE"])
@authenticate
@authorize(Role.ADMIN)
def delete_user(user_id):
    try:
        admin_service.delete_user(user_id)
        return jsonify({
            "message": "User deleted successfully"
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


# ==========================================
# Venue Management Routes (Admin Only)
# ==========================================

@admin_controller.route("/venues", methods=["POST"])
@authenticate
@authorize(Role.ADMIN)
def create_venue():
    data = request.get_json() or {}
    try:
        return jsonify(venue_service.create_venue(data).to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/venues/<int:venue_id>", methods=["PUT", "PATCH"])
@authenticate
@authorize(Role.ADMIN)
def update_venue(venue_id):
    data = request.get_json() or {}
    data["venue_id"] = venue_id
    try:
        venue = venue_service.update_venue(data)
        return jsonify({
            "message": "Venue updated successfully",
            "venue": venue.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/venues/<int:venue_id>", methods=["DELETE"])
@authenticate
@authorize(Role.ADMIN)
def delete_venue(venue_id):
    try:
        return jsonify(venue_service.delete_venue(venue_id)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


# ==========================================
# Event Management Routes (Admin Only)
# ==========================================

@admin_controller.route("/events", methods=["POST"])
@authenticate
@authorize(Role.ADMIN)
def create_event():
    """Endpoint for admins to create an event."""
    data = request.get_json() or {}
    try:
        event = event_service.create_event(data)
        return jsonify({
            "message": "Event created successfully",
            "event": event.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/events/<int:event_id>", methods=["PUT", "PATCH"])
@authenticate
@authorize(Role.ADMIN)
def update_event(event_id):
    """Endpoint for admins to update an event."""
    data = request.get_json() or {}
    data["event_id"] = event_id
    try:
        event = event_service.update_event(data)
        return jsonify({
            "message": "Event updated successfully",
            "event": event.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/events/<int:event_id>", methods=["DELETE"])
@authenticate
@authorize(Role.ADMIN)
def delete_event(event_id):
    """Endpoint for admins to delete an event."""
    try:
        event_service.delete_event(event_id)
        return jsonify({
            "message": "Event deleted successfully"
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/events/<int:event_id>/genres/<int:genre_id>", methods=["POST"])
@authenticate
@authorize(Role.ADMIN)
def add_genre_to_event(event_id, genre_id):
    """Endpoint for admins to link a genre to an event."""
    try:
        event_service.add_genre_to_event(event_id, genre_id)
        return jsonify({
            "message": "Genre linked to event successfully"
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


# ==========================================
# Schedule Management Routes (Admin Only)
# ==========================================

@admin_controller.route("/schedules", methods=["POST"])
@authenticate
@authorize(Role.ADMIN)
def create_schedule():
    """Endpoint for admins to create an event schedule."""
    data = request.get_json() or {}
    try:
        schedule = schedule_service.create_schedule(data)
        return jsonify({
            "message": "Event schedule created successfully",
            "schedule": schedule.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/schedules/<int:schedule_id>", methods=["PUT", "PATCH"])
@authenticate
@authorize(Role.ADMIN)
def update_schedule(schedule_id):
    """Endpoint for admins to update an event schedule."""
    data = request.get_json() or {}
    data["schedule_id"] = schedule_id
    try:
        schedule = schedule_service.update_schedule(data)
        return jsonify({
            "message": "Event schedule updated successfully",
            "schedule": schedule.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/schedules/<int:schedule_id>", methods=["DELETE"])
@authenticate
@authorize(Role.ADMIN)
def delete_schedule(schedule_id):
    """Endpoint for admins to delete an event schedule."""
    try:
        schedule_service.delete_schedule(schedule_id)
        return jsonify({
            "message": "Event schedule deleted successfully"
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


# ==========================================
# Booking Oversight Routes (Admin Only)
# ==========================================

@admin_controller.route("/bookings", methods=["GET"])
@authenticate
@authorize(Role.ADMIN)
def get_all_bookings():
    """Endpoint for admins to list all bookings system-wide."""
    try:
        bookings = booking_service.get_all_bookings()
        return jsonify([b.to_dict() for b in bookings]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@admin_controller.route("/bookings/<int:booking_id>", methods=["GET"])
@authenticate
@authorize(Role.ADMIN)
def get_admin_booking_by_id(booking_id):
    """Endpoint for admins to view details of any booking."""
    try:
        booking = booking_service.get_booking_by_id(booking_id)
        return jsonify(booking.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
