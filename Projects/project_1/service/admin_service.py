
import re
from werkzeug.security import generate_password_hash

PHONE_REGEX = r"^\+?[0-9]{7,15}$"


class AdminService:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_all_users(self):
        return self.user_dao.get_all_users()

    def update_user(self, data):
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("user_id is required for user details")

        user = self.user_dao.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        if "username" in data and data["username"]:
            user.username = data["username"].strip() if isinstance(data["username"], str) else data["username"]
        if "email" in data and data["email"]:
            user.email = data["email"].strip() if isinstance(data["email"], str) else data["email"]
        if "phone_no" in data:
            phone_val = data["phone_no"]
            if phone_val and str(phone_val).strip():
                phone_clean = str(phone_val).strip()
                if not re.match(PHONE_REGEX, phone_clean):
                    raise ValueError("Invalid phone number format. Must contain 7-15 digits with optional '+' prefix.")
                user.phone_no = phone_clean
            else:
                user.phone_no = None
        if "password" in data and data["password"]:
            user.password_hash = generate_password_hash(data["password"])
        if "is_active" in data:
            user.is_active = bool(data["is_active"])
        if "role" in data and data["role"]:
            user.role = data["role"]

        return self.user_dao.update_user(user)

    def delete_user(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        return self.user_dao.delete_user(user)
