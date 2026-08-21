"""
Booking Controller.
"""

from flask import Blueprint, request, jsonify
from service.booking_service import BookingService
from dao.booking_dao import BookingDAO
from common.decorators import authenticate
from flask import g

booking_controller = Blueprint("booking_controller", __name__)
booking_service = BookingService(BookingDAO())


@booking_controller.route("/", methods=["GET"])
@authenticate
def get_bookings():
    """Endpoint to list bookings."""
    # return jsonify([]), 200
    return jsonify({
        "message": f"Hello User #{g.current_user['user_id']} with role '{g.current_user['role']}'! Here are your bookings.",
        "bookings": []
    }), 200


@booking_controller.route("/", methods=["POST"])
def create_booking():
    """Endpoint to create a booking."""
    data = request.get_json() or {}
    try:
        booking = booking_service.create_booking(data)
        return jsonify({
            "message": "Booking created successfully",
            "booking": booking.to_dict() if booking else None
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
