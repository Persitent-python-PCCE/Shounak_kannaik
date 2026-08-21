"""
Booking Controller.

Provides endpoints for booking retrieval, cancellation, and ticket reservations.
"""

from flask import Blueprint, request, jsonify, g
from service.booking_service import BookingService
from dao.booking_dao import BookingDAO
from common.decorators import authenticate

booking_controller = Blueprint("booking_controller", __name__)
booking_service = BookingService(BookingDAO())


@booking_controller.route("/", methods=["GET"])
@authenticate
def get_bookings():
    """Endpoint to list bookings for the authenticated user."""
    user_id = g.current_user.get("user_id")
    try:
        bookings = booking_service.get_bookings_for_user(user_id)
        return jsonify([b.to_dict() for b in bookings]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@booking_controller.route("/<int:booking_id>", methods=["GET"])
@authenticate
def get_booking_by_id(booking_id):
    """Endpoint to get a specific booking by ID."""
    try:
        booking = booking_service.get_booking_by_id(booking_id)
        user_id = g.current_user.get("user_id")
        user_role = g.current_user.get("role")
        if booking.user_id != user_id and user_role != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        return jsonify(booking.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@booking_controller.route("/", methods=["POST"])
@authenticate
def create_booking():
    # TODO: implement manually — this is the seat-locking transaction
    # (SELECT FOR UPDATE, atomic Booking + BookingItem creation,
    # rollback on conflict). Being written by hand intentionally.
    return jsonify({"error": "not implemented"}), 501


@booking_controller.route("/<int:booking_id>/cancel", methods=["PATCH"])
@authenticate
def cancel_booking(booking_id):
    """Endpoint to cancel a booking."""
    try:
        booking = booking_service.get_booking_by_id(booking_id)
        user_id = g.current_user.get("user_id")
        user_role = g.current_user.get("role")
        if booking.user_id != user_id and user_role != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        updated_booking = booking_service.cancel_booking(booking_id)
        return jsonify({
            "message": "Booking cancelled successfully",
            "booking": updated_booking.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
