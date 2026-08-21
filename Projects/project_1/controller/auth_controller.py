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
    user = auth_service.login(data)
    token = auth_service.generate_token(user)
    return jsonify({
        "message": "User logged in successfully",
        "token": token,
        "user": user.to_dict() if user else None,
    }), 200


@auth_controller.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    user = auth_service.register(data)
    return jsonify({
        "message": "User created successfully",
        "user": user.to_dict() if user else None
    }), 201
