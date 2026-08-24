
from flask import Blueprint, request, jsonify
from service.auth_service import AuthService
from service.document_service import DocumentService
from dao.user_dao import UserDAO
from dao.document_dao import DocumentDAO
from common.file_utils import validate_file, save_uploaded_file

auth_controller = Blueprint("auth_controller", __name__)
auth_service = AuthService(UserDAO())
document_service = DocumentService(DocumentDAO())


@auth_controller.route("/login", methods=["POST"])
def user_login():
    data = request.get_json() or request.form.to_dict() or {}
    try:
        user = auth_service.login(data)
        token = auth_service.generate_token(user)
        return jsonify({
            "message": "User logged in successfully",
            "token": token,
            "user": user.to_dict() if user else None,
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_controller.route("/register", methods=["POST"])
def register():

    data = request.form.to_dict() if request.form else (request.get_json() or {})
    id_file = request.files.get("id_document") or request.files.get("file") or request.files.get("document")
    doc_type = data.get("doc_type", "Govt ID")

    try:

        if id_file and getattr(id_file, "filename", None):
            validate_file(
                id_file,
                allowed_extensions={"pdf", "png", "jpg", "jpeg"},
                max_size_bytes=5 * 1024 * 1024,
                required=False
            )


        user = auth_service.register(data)


        document = None
        if id_file and getattr(id_file, "filename", None):
            file_path = save_uploaded_file(id_file, "static/uploads/id_docs", prefix=f"user_{user.id}")
            document = document_service.upload_document(user.id, doc_type, file_path)

        res = {
            "message": "User created successfully",
            "user": user.to_dict() if user else None,
        }
        if document:
            res["document"] = document.to_dict()

        return jsonify(res), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
