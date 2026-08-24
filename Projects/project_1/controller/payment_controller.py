
from flask import Blueprint, jsonify
from service.payment_service import PaymentService
from dao.payment_dao import PaymentDAO

payment_controller = Blueprint("payment_controller", __name__)
payment_service = PaymentService(PaymentDAO())


@payment_controller.route("/modes", methods=["GET"])
def get_payment_modes():
    try:
        modes = payment_service.get_all_payment_modes()
        return jsonify([m.to_dict() for m in modes]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@payment_controller.route("/statuses", methods=["GET"])
def get_payment_statuses():
    try:
        statuses = payment_service.get_all_payment_statuses()
        return jsonify([s.to_dict() for s in statuses]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
