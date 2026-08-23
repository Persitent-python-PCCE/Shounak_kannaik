"""
Authentication Web UI Controller.

Handles HTML views and form submissions for customer registration, login, and logout.
Sets and deletes JWT access token cookies.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from service.auth_service import AuthService
from service.document_service import DocumentService
from dao.user_dao import UserDAO
from dao.document_dao import DocumentDAO
from common.file_utils import validate_file, save_uploaded_file
from forms.auth_forms import LoginForm, RegisterForm

auth_web = Blueprint("auth_web", __name__)
auth_service = AuthService(UserDAO())
document_service = DocumentService(DocumentDAO())


@auth_web.route("/register", methods=["GET"])
def register():
    """Display registration form with ID document upload."""
    form = RegisterForm()
    return render_template("auth/register.html", form=form)


@auth_web.route("/register", methods=["POST"])
def process_register():
    """
    Process user registration.
    Enforces validate-file-before-user-creation discipline.
    """
    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template("auth/register.html", form=form)

    # 1. Create user
    try:
        user_data = {
            "username": form.username.data.strip(),
            "email": form.email.data.strip(),
            "password": form.password.data,
            "phone_no": form.phone_no.data.strip() if form.phone_no.data else None
        }
        user = auth_service.register(user_data)

        # 2. Upload document if provided
        id_file = form.id_document.data
        if id_file and getattr(id_file, "filename", None):
            try:
                validate_file(
                    id_file,
                    allowed_extensions={"pdf", "png", "jpg", "jpeg"},
                    max_size_bytes=5 * 1024 * 1024,
                    required=False
                )
                file_path = save_uploaded_file(id_file, "static/uploads/id_docs", prefix=f"user_{user.id}")
                document_service.upload_document(user.id, form.doc_type.data or "Govt ID", file_path)
            except Exception as doc_err:
                flash(f"Account created, but document upload failed: {str(doc_err)}", "warning")
                return redirect(url_for("auth_web.login"))

        flash("Registration successful! Please log in to continue.", "success")
        return redirect(url_for("auth_web.login"))

    except ValueError as e:
        flash(str(e), "danger")
        return render_template("auth/register.html", form=form)
    except Exception as e:
        flash(f"An error occurred during registration: {str(e)}", "danger")
        return render_template("auth/register.html", form=form)


@auth_web.route("/login", methods=["GET"])
def login():
    """Display login form."""
    form = LoginForm()
    return render_template("auth/login.html", form=form)


@auth_web.route("/login", methods=["POST"])
def process_login():
    """Process login, generate JWT, and set auth cookie."""
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("auth/login.html", form=form)

    try:
        user = auth_service.login({
            "username": form.username.data.strip(),
            "password": form.password.data
        })
        token = auth_service.generate_token(user)

        flash(f"Welcome back, {user.username}!", "success")
        if user.role and str(user.role).lower() == "admin":
            response = make_response(redirect(url_for("admin_web.dashboard")))
        else:
            response = make_response(redirect(url_for("events_web.list_events")))
        response.set_cookie("access_token_cookie", token, httponly=True, samesite="Lax")
        return response

    except Exception as e:
        flash(str(e), "danger")
        return render_template("auth/login.html", form=form)


@auth_web.route("/logout", methods=["POST"])
def logout():
    """Clear auth cookies and redirect to login."""
    flash("You have been successfully logged out.", "info")
    response = make_response(redirect(url_for("auth_web.login")))
    response.delete_cookie("access_token_cookie")
    return response
