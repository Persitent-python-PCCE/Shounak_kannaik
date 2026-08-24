from common.exceptions import (
    ResourceNotFoundError,
    AuthenticationError,
    AuthorizationError,
    SeatUnavailableError,
)
from flask import Blueprint, request, jsonify, g
from service.booking_service import BookingService
from dao.booking_dao import BookingDAO
from common.decorators import authenticate

booking_controller = Blueprint("booking_controller", __name__)
booking_service = BookingService(BookingDAO())


@booking_controller.route("/", methods=["GET"])
@authenticate
def get_bookings():
    user_id = g.current_user.get("user_id")
    try:
        bookings = booking_service.get_bookings_for_user(user_id)
        return jsonify([b.to_dict() for b in bookings]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@booking_controller.route("/<int:booking_id>", methods=["GET"])
@authenticate
def get_booking_by_id(booking_id):
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
    user_id = g.current_user.get("user_id")
    data = request.get_json()
    schedule_id = data.get("schedule_id")
    seat_ids = data.get("seat_ids")
    payment_mode_id = data.get("payment_mode_id")
    if not schedule_id or not seat_ids:
        error = ResourceNotFoundError("Please provide a valid schedule ID and seat IDs.")
        return jsonify(
            {"message": error.message, "status_code": error.status_code}
        ), error.status_code
    if data.get("user_id") != user_id:
        error = AuthenticationError("Unauthorized")
        return jsonify(
            {"message": error.message, "status_code": error.status_code}
        ), error.status_code
    try:
        booking = booking_service.create_booking(
            user_id = user_id,
            schedule_id = schedule_id,
            seat_ids = seat_ids,
            payment_mode_id = payment_mode_id
        ) 
        return jsonify({"message": "Booking created successfully", "booking": booking.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SeatUnavailableError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@booking_controller.route("/<int:booking_id>/cancel", methods=["PATCH"])
@authenticate
def cancel_booking(booking_id):
    user_id = g.current_user.get("user_id")
    user_role = g.current_user.get("role")
    try:
        updated_booking = booking_service.cancel_booking(
            booking_id=booking_id,
            user_id=user_id,
            role=user_role
        )
        return jsonify({
            "message": "Booking cancelled successfully",
            "booking": updated_booking.to_dict()
        }), 200
    except AuthorizationError as e:
        return jsonify({"error": str(e)}), e.status_code
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
