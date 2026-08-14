from service.user_service import UserService
from models.user_models import CreateUserRequest, UserloginRequest, UserLoginResponse
from models.user_models import ShowAllUsersResponse
from models.user_models import SearchUserRequest, SearchUserResponse
from models.user_models import UpdateUserRequest, UpdateUserResponse
from models.user_models import DeleteUserRequest, DeleteUserResponse

class UserController:
    def __init__(self):
        self.user_service = UserService()
    
    def create_user(self):
        name = input("enter your name: ")
        username = input("Create username: ")
        email = input("Enter your email: ")
        password = input("enter password: ")
        while True:
            conf_password = input("confirm password: ")
            if password == conf_password:
                break
            else:
                print("password doesnt match. try again") 
        
        user = CreateUserRequest(username=username, name=name, email=email, password=password)
        responseObj = self.user_service.create_user(user)
        
        if responseObj.error_message is None:
            print(f"User created successfully! {responseObj.user_id}")
        else:
            print(f"Error: {responseObj.error_message}")
    
    def user_login(self) -> UserLoginResponse:
        while True:
            username = input("Enter username (or 0 to cancel): ")
            if username == "0":
                return None
            password = input("enter password: ")
            user = UserloginRequest(username=username,password=password)
            
            responseObj = self.user_service.user_login(user)
            if responseObj.error_message is None:
                print(f"Login Successfull! Welcome {responseObj.username}!\n")
                return responseObj
            else:
                print(f"Error: {responseObj.error_message}")
    
    def show_all_users(self)-> list[ShowAllUsersResponse]:
        users = self.user_service.show_all_users()
        if users:
            print(f'------------- All users: total: {len(users)} -------------')
            for i, user in enumerate(users):
                print(f"{i}. user_id: {user.user_id}\tusername: {user.username}\tname: {user.name}\temail: {user.email}\trole: {user.role}")
                
            
    def search_user(self):
        username = input("Enter username to search (or 0 to cancel): ")
        if username == "0":
            return
            
        user = SearchUserRequest(username=username)
        
        response_obj = self.user_service.search_user(user)
        if response_obj.error_message is None:
            print(f"user found!")
            print(f'user_id: {response_obj.user_id}\t|\tusername: {response_obj.username}\t|\tname: {response_obj.name}\t|\temail: {response_obj.email}\t|\trole: {response_obj.role}')
        else:
            print(f"Error: {response_obj.error_message}")
    
    def update_user(self):
        self.show_all_users()
        user_id = int(input("Enter the user_id to update: "))
        print("Enter the new details (if no updates required then leave blank)")
        name = input("Update Name: ")
        username = input("Update Username: ")
        email = input("Update email: ")
        password = input("Update password: ")
        role = input("Update Role (admin, customer): ")
        
        user = UpdateUserRequest(user_id=user_id, username=username, name=name, email=email, password=password, role=role)
        response_obj = self.user_service.update_user(user)
        
        if response_obj.affected_rows != 0 and response_obj.error_message is None:
            print("User updated successfully")
        else:
            print(f"Error: {response_obj.error_message}")

    def delete_user(self):
        self.show_all_users()
        user_id = int(input("Enter the user_id to delete: "))
        confirm = input(f"Are you sure you want to delete user with user_id {user_id}? (yes/no): ")
        if confirm.lower() != "yes":
            print("Delete cancelled.")
            return
        user = DeleteUserRequest(user_id=user_id)
        response_obj = self.user_service.delete_user(user)
        if response_obj.affected_rows is not None and response_obj.error_message is None:
            print(f"User with user_id {user_id} deleted successfully.")
        else:
            print(f"Error: {response_obj.error_message}")