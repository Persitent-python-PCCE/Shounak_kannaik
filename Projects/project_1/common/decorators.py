"""
Custom route decorators for authentication and role-based access control (RBAC).
"""
from functools import wraps
from flask import request, g
from common.exceptions import AuthenticationError
from service.auth_service import AuthService
from dao.user_dao import UserDAO

auth_service = AuthService(UserDAO())


def authenticate(f):
    """
    Decorator to ensure the requesting user is authenticated.
    Redirects unauthenticated users to the login page or returns a 401 response.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationError("Authorization header is missing")
        parts = auth_header.strip().split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationError("Invalid Authorization header format")
        token = parts[1]
        payload= auth_service.verify_token(token)
        g.current_user ={
            "user_id": payload.get("user_id"),
            "role": payload.get("role")
        }
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to restrict access to administrator users only.
    Returns 403 Forbidden or redirects if the current user lacks admin privileges.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implementation to verify current_user.is_admin / role will go here
        return f(*args, **kwargs)
    return decorated_function
