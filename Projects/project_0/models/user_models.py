class CreateUserRequest:
    def __init__(self, username: str, name:str, email:str, password:str, role="customer"):
        self.username = username
        self.name = name
        self.email = email
        self.password= password
        self.role = role

class CreateUserResponse:
    def __init__(self, user_id: int, error_message: str):
        self.user_id = user_id
        self.error_message = error_message
        
class UserloginRequest:
    def __init__(self, username: str, password:str):
        self.username = username
        self.password = password

class UserLoginResponse:
    def __init__(self, login_status: int, user_id: int, username: str, role: str, error_message: str):
        self.login_status = login_status
        self.user_id = user_id 
        self.username = username
        self.role = role
        self.error_message = error_message
        
class ShowAllUsersResponse:
    def __init__(self, user_id: int,username: str, name:str, email:str, role: str):
        self.user_id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.role = role
        

class SearchUserRequest:
    def __init__(self, username: str):
        self.username = username

class SearchUserResponse:
    def __init__(self, user_id: int,username: str, name:str, email:str, role: str, error_message: str):
            self.user_id = user_id
            self.username = username
            self.name = name
            self.email = email
            self.role = role
            self.error_message = error_message

class UpdateUserRequest:
    def __init__(self, user_id: int, username: str, name: str, email: str, password: str, role: str):
        self.user_id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        
class UpdateUserResponse:
    def __init__(self, affected_rows: int, error_message: str):
        self.affected_rows = affected_rows
        self.error_message = error_message

class DeleteUserRequest:
    def __init__(self, user_id: int):
        self.user_id = user_id

class DeleteUserResponse:
    def __init__(self, affected_rows: int, error_message: str):
        self.affected_rows = affected_rows
        self.error_message = error_message