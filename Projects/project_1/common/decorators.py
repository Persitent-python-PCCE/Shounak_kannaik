from functools import wraps
from flask import request, g
from common.exceptions import AuthenticationError, AuthorizationError
from service.auth_service import AuthService
from common.roles import Role
from dao.user_dao import UserDAO

auth_service = AuthService(UserDAO())


def authenticate(f):
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


def authorize(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "current_user") or not g.current_user:
                raise AuthenticationError("Authentication required before Authorization")
            user_role = g.current_user.get("role")
            if user_role not in allowed_roles:
                raise AuthorizationError(f"Unauthorized. Allowed roles: {', '.join(allowed_roles)}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
