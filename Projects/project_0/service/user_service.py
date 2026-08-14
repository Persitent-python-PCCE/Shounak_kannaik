from DAO.user_dao import UserDAO
from models.user_models import CreateUserRequest, CreateUserResponse, UserloginRequest, UserLoginResponse
from models.user_models import ShowAllUsersResponse
from models.user_models import SearchUserRequest, SearchUserResponse
from models.user_models import UpdateUserRequest, UpdateUserResponse
from models.user_models import DeleteUserRequest, DeleteUserResponse
import re
import hashlib

class UserService:
    def __init__(self):
        self.user_dao = UserDAO()
        
    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def create_user(self, user: CreateUserRequest)->CreateUserResponse:
        try:
            # Standardize inputs
            user.username = user.username.strip().lower() if user.username else ""
            user.name = " ".join(user.name.strip().split()).title() if user.name else ""
            user.email = user.email.strip().lower() if user.email else ""
            raw_password = user.password.strip() if user.password else ""
            user.role = user.role.strip().lower() if user.role and user.role.strip() else "customer"

            # Username validation
            if user.username == "":
                raise ValueError("username cant be empty")

            # Password validation
            password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if re.fullmatch(password_pattern, raw_password) is None:
                raise ValueError("Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character (@$!%*?&)")
            user.password = self._hash_password(raw_password)

            # Email validation
            pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
            if re.fullmatch(pattern, user.email) is None:
                raise ValueError("Enter valid email id")
        except Exception as e:
            return CreateUserResponse(None, str(e))
        return self.user_dao.create_user(user=user)
    
    def user_login(self, user: UserloginRequest) -> UserLoginResponse:
        try:
            user.username = user.username.strip().lower() if user.username else ""
            raw_password = user.password.strip() if user.password else ""

            if user.username == "":
                raise ValueError("username cant be empty")
            if raw_password == "":
                raise ValueError("password cant be empty")
            
            user.password = self._hash_password(raw_password)
        except ValueError as e:
            return UserLoginResponse(None, None, None, None, str(e))
        return self.user_dao.user_login(user=user)
    
    def show_all_users(self)-> list[ShowAllUsersResponse]:
        return self.user_dao.show_all_users()
    
    def search_user(self, user: SearchUserRequest) -> SearchUserResponse:
        try:
            user.username = user.username.strip().lower() if user.username else ""
            if user.username == "":
                raise ValueError("username cant be empty")
        except ValueError as e:
            return SearchUserResponse(None, None, None, None, None, str(e))
        return self.user_dao.search_user(user=user)
    
    def update_user(self, user: UpdateUserRequest) -> UpdateUserResponse:
        try:
            if user.username is not None and user.username.strip() != "":
                user.username = user.username.strip().lower()
            if user.name is not None and user.name.strip() != "":
                user.name = " ".join(user.name.strip().split()).title()
            if user.email is not None and user.email.strip() != "":
                user.email = user.email.strip().lower()
                pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
                if re.fullmatch(pattern, user.email) is None:
                    raise ValueError("Enter valid email id")
            if user.password is not None and user.password.strip() != "":
                raw_password = user.password.strip()
                password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
                if re.fullmatch(password_pattern, raw_password) is None:
                    raise ValueError("Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character (@$!%*?&)")
                user.password = self._hash_password(raw_password)
            if user.role is not None and user.role.strip() != "":
                user.role = user.role.strip().lower()
        except ValueError as e:
            return UpdateUserResponse(None, str(e))
        return self.user_dao.update_user(user=user)

    def delete_user(self, user: DeleteUserRequest) -> DeleteUserResponse:
        try:
            if user.user_id is None:
                raise ValueError("user_id cannot be empty")
        except ValueError as e:
            return DeleteUserResponse(None, str(e))
        return self.user_dao.delete_user(user=user)
        