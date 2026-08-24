
from functools import wraps
from flask import request, redirect, url_for, render_template, g
from common.exceptions import AuthenticationError, AuthorizationError
from service.auth_service import AuthService
from dao.user_dao import UserDAO

auth_service = AuthService(UserDAO())


def get_token_from_request():
    token = request.cookies.get("access_token_cookie")
    if token:
        return token

    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.strip().split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
    return None


def ui_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return redirect(url_for("auth_web.login"))
        try:
            payload = auth_service.verify_token(token)
            g.current_user = {
                "user_id": payload.get("user_id"),
                "role": payload.get("role")
            }
        except AuthenticationError:
            return redirect(url_for("auth_web.login"))
        except Exception:
            return redirect(url_for("auth_web.login"))
        return f(*args, **kwargs)
    return decorated_function


def ui_role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = get_token_from_request()
            if not token:
                return redirect(url_for("auth_web.login"))
            try:
                payload = auth_service.verify_token(token)
                g.current_user = {
                    "user_id": payload.get("user_id"),
                    "role": payload.get("role")
                }
            except AuthenticationError:
                return redirect(url_for("auth_web.login"))
            except Exception:
                return redirect(url_for("auth_web.login"))

            user_role = g.current_user.get("role")
            if user_role not in allowed_roles:
                return render_template("403.html"), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
