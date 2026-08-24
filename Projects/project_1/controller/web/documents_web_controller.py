
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from service.document_service import DocumentService
from dao.document_dao import DocumentDAO
from common.ui_decorators import ui_login_required
from common.file_utils import validate_file, save_uploaded_file
from forms.document_forms import DocumentUploadForm

documents_web = Blueprint("documents_web", __name__)
document_service = DocumentService(DocumentDAO())


@documents_web.route("/documents", methods=["GET"])
@ui_login_required
def list_documents():
    user_id = g.current_user.get("user_id")
    documents = document_service.get_documents_for_user(user_id)
    form = DocumentUploadForm()
    return render_template("documents/list.html", documents=documents, form=form)


@documents_web.route("/documents/upload", methods=["POST"])
@ui_login_required
def upload_document_ui():
    user_id = g.current_user.get("user_id")
    form = DocumentUploadForm()

    if not form.validate_on_submit():
        documents = document_service.get_documents_for_user(user_id)
        return render_template("documents/list.html", documents=documents, form=form)

    doc_file = form.document.data
    doc_type = form.doc_type.data or "Govt ID"

    try:
        validate_file(
            doc_file,
            allowed_extensions={"pdf", "png", "jpg", "jpeg"},
            max_size_bytes=5 * 1024 * 1024,
            required=True
        )
        saved_path = save_uploaded_file(doc_file, "static/uploads/id_docs", prefix=f"user_{user_id}")
        document_service.upload_document(user_id, doc_type, saved_path)

        flash("Document uploaded successfully!", "success")
        return redirect(url_for("documents_web.list_documents"))

    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Upload failed: {str(e)}", "danger")

    return redirect(url_for("documents_web.list_documents"))
