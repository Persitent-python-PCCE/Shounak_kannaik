"""
Authentication Controller.
"""

from flask import Blueprint, request, jsonify
from service.auth_service import AuthService
from dao.user_dao import UserDAO

auth_controller = Blueprint("auth_controller", __name__)
auth_service = AuthService(UserDAO())


@auth_controller.route("/login", methods=["POST"])
def user_login():
    data = request.get_json() or {}
    try:
        user = auth_service.login(data)
        return jsonify({
            "message": "User logged in successfully",
            "user": user.to_dict() if user else None
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@auth_controller.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    try:
        user = auth_service.register(data)
        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict() if user else None
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
