"""
Admin Service.

Handles administrative workflows, reporting, user management, and system configuration.
Receives DAOs via constructor injection to facilitate unit testing with mock DAOs.
"""

from werkzeug.security import generate_password_hash


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
            user.username = data["username"]
        if "email" in data and data["email"]:
            user.email = data["email"]
        if "phone_no" in data and data["phone_no"]:
            user.phone_no = data["phone_no"]
        if "password" in data and data["password"]:
            user.password_hash = generate_password_hash(data["password"])
        if "is_active" in data and data["is_active"]:
            user.is_active = data["is_active"]
        if "role" in data and data["role"]:
            user.role = data["role"]
        
        return self.user_dao.update_user(user)

    def delete_user(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        return self.user_dao.delete_user(user)
    
    