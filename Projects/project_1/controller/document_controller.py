
from flask import Blueprint, request, jsonify, g
from service.document_service import DocumentService
from dao.document_dao import DocumentDAO
from common.decorators import authenticate
from common.file_utils import validate_file, save_uploaded_file

document_controller = Blueprint("document_controller", __name__)
document_service = DocumentService(DocumentDAO())


@document_controller.route("/", methods=["GET"])
@authenticate
def get_user_documents():
    user_id = g.current_user.get("user_id")
    try:
        documents = document_service.get_documents_for_user(user_id)
        return jsonify([d.to_dict() for d in documents]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@document_controller.route("/<int:document_id>", methods=["GET"])
@authenticate
def get_document_by_id(document_id):
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
@authenticate
def upload_document():
    user_id = g.current_user.get("user_id")
    id_file = request.files.get("id_document") or request.files.get("file") or request.files.get("document")
    doc_type = request.form.get("doc_type", "Govt ID")

    try:
        validate_file(
            id_file,
            allowed_extensions={"pdf", "png", "jpg", "jpeg"},
            max_size_bytes=5 * 1024 * 1024,
            required=True
        )
        saved_path = save_uploaded_file(id_file, "static/uploads/id_docs", prefix=f"user_{user_id}")
        doc = document_service.upload_document(user_id, doc_type, saved_path)
        return jsonify({
            "message": "Document uploaded successfully",
            "document": doc.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
