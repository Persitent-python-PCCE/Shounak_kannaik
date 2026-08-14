from DAO.user_dao import UserDAO
from models.user_models import CreateUserRequest, CreateUserResponse, UserloginRequest, UserLoginResponse
from models.user_models import ShowAllUsersResponse
from models.user_models import SearchUserRequest, SearchUserResponse
from models.user_models import UpdateUserRequest, UpdateUserResponse
from models.user_models import DeleteUserRequest, DeleteUserResponse
import re

class UserService:
    def __init__(self):
        self.user_dao = UserDAO()
        
    def create_user(self, user: CreateUserRequest)->CreateUserResponse:
        #username validation
        try:
            if user.username.strip() == "": raise ValueError("username cant be empty")

            #email validation
            pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
            if re.fullmatch(pattern, user.email.strip()) is None: raise ValueError("Enter valid email id")
        except Exception as e:
            return CreateUserResponse(None, str(e))
        return self.user_dao.create_user(user=user)
    
    def user_login(self, user: UserloginRequest) -> UserLoginResponse:
        try:
            if user.username.strip() == "": raise ValueError("username cant be empty")
            if user.password.strip() == "": raise ValueError("password cant be empty")
        except ValueError as e:
            return UserLoginResponse(None, None, None, None, str(e))
        return self.user_dao.user_login(user=user)
    
    def show_all_users(self)-> list[ShowAllUsersResponse]:
        return self.user_dao.show_all_users()
    
    def search_user(self, user: SearchUserRequest) -> SearchUserResponse:
        try:
            if user.username.strip() == "": raise ValueError("username cant be empty")
        except ValueError as e:
            return SearchUserResponse(None, None, None, None, None, str(e))
        return self.user_dao.search_user(user=user)
    
    def update_user(self, user:UpdateUserRequest) -> UpdateUserResponse:
        try:
            if user.email != "":
                pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
                if re.fullmatch(pattern, user.email.strip()) is None: raise ValueError("Enter valid email id")
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
        