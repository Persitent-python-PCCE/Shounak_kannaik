"""
Admin Controller.
"""

from flask import Blueprint, request, jsonify
from service.admin_service import AdminService
from service.venue_service import VenueService
from dao.user_dao import UserDAO
from dao.venue_dao import VenueDAO

admin_controller = Blueprint("admin_controller", __name__)
admin_service = AdminService(UserDAO())
venue_service = VenueService(VenueDAO())


@admin_controller.route("/users", methods=["GET"])
def get_users():
    """Endpoint to list all users."""
    try:
        users = admin_service.get_all_users()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500

@admin_controller.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
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
    
@admin_controller.route("/venues", methods=["POST"])
def create_venue():
    data = request.get_json() or {}
    try:
        return jsonify(venue_service.create_venue(data).to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500

@admin_controller.route("/venues/<int:venue_id>", methods=["PUT", "PATCH"])
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
def delete_venue(venue_id):
    try:
        return jsonify(venue_service.delete_venue(venue_id)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500



