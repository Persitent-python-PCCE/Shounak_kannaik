"""
Document Controller.

Provides endpoints for managing and retrieving user KYC/verification documents.
"""

from flask import Blueprint, jsonify, g
from service.document_service import DocumentService
from dao.document_dao import DocumentDAO
from common.decorators import authenticate

document_controller = Blueprint("document_controller", __name__)
document_service = DocumentService(DocumentDAO())


@document_controller.route("/", methods=["GET"])
@authenticate
def get_user_documents():
    """Endpoint to list documents belonging to the authenticated user."""
    user_id = g.current_user.get("user_id")
    try:
        documents = document_service.get_documents_for_user(user_id)
        return jsonify([d.to_dict() for d in documents]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@document_controller.route("/<int:document_id>", methods=["GET"])
@authenticate
def get_document_by_id(document_id):
    """Endpoint to get a specific document by ID."""
    try:
        document = document_service.get_document_by_id(document_id)
        user_id = g.current_user.get("user_id")
        user_role = g.current_user.get("role")
        if document.user_id != user_id and user_role != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        return jsonify(document.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@document_controller.route("/upload", methods=["POST"])
def upload_document():
    # TODO: implement manually — file upload validation and storage
    # via common/file_utils. Intentionally left for manual implementation.
    return jsonify({"error": "not implemented"}), 501
