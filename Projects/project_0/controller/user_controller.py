from service.user_service import UserService
from models.user_models import CreateUserRequest, UserloginRequest, UserLoginResponse
from models.user_models import ShowAllUsersResponse
from models.user_models import SearchUserRequest, SearchUserResponse
from models.user_models import UpdateUserRequest, UpdateUserResponse
from models.user_models import DeleteUserRequest, DeleteUserResponse
from utils.ui import clear_screen, pause
from utils.logger import logger

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
            logger.info(f"User created successfully: {username} (ID: {responseObj.user_id})")
            print(f"User created successfully! {responseObj.user_id}")
        else:
            logger.warning(f"Failed to create user {username}: {responseObj.error_message}")
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
                logger.info(f"User login successful: {username}")
                print(f"Login Successfull! Welcome {responseObj.username}!\n")
                return responseObj
            else:
                logger.warning(f"Failed login attempt for {username}: {responseObj.error_message}")
                print(f"Error: {responseObj.error_message}")
    
    def show_all_users(self)-> list[ShowAllUsersResponse]:
        users = self.user_service.show_all_users()
        if users:
            print(f'------------- All users: total: {len(users)} -------------')
            for i, user in enumerate(users):
                print(f"{i}. user_id: {user.user_id}\tusername: {user.username}\tname: {user.name}\temail: {user.email}\trole: {user.role}")
                
            
    def search_user(self):
        username = input("Enter username to search (or 0 to go back): ")
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
        try:
            user_id = int(input("Enter the user_id to update: "))
        except ValueError:
            print("Invalid user_id.")
            pause()
            return
        print("Enter the new details (if no updates required then leave blank)")
        name = input("Update Name: ")
        username = input("Update Username: ")
        email = input("Update email: ")
        password = input("Update password: ")
        role = input("Update Role (admin, customer): ")
        
        user = UpdateUserRequest(user_id=user_id, username=username, name=name, email=email, password=password, role=role)
        responseObj = self.user_service.update_user(user)
        
        if responseObj.affected_rows is not None and responseObj.error_message is None:
            logger.info(f"User {user_id} updated successfully by Admin.")
            print("user updated successfully.")
        else:
            logger.error(f"Failed to update user {user_id}: {responseObj.error_message}")
            print(f"Error: {responseObj.error_message}")

    def delete_user(self):
        self.show_all_users()
        try:
            user_id = int(input("Enter the user_id to delete: "))
        except ValueError:
            print("Invalid user_id.")
            pause()
            return
        confirm = input(f"Are you sure you want to delete user with user_id {user_id}? (yes/no): ")
        if confirm.lower() != "yes":
            print("Delete cancelled.")
            return
        user = DeleteUserRequest(user_id=user_id)
        responseObj = self.user_service.delete_user(user)
        if responseObj.affected_rows is not None and responseObj.error_message is None:
            logger.info(f"User {user_id} deleted successfully by Admin.")
            print(f"User with user_id {user_id} deleted successfully.")
        else:
            logger.error(f"Failed to delete user {user_id}: {responseObj.error_message}")
            print(f"Error: {responseObj.error_message}")

    def show_profile(self, current_user):
        """Display the logged-in user's profile details."""
        clear_screen()
        # Fetch full profile via username search
        user = self.user_service.search_user(SearchUserRequest(username=current_user.username))
        print()
        print('  ─' * 30)
        print(f'  {"My Profile":^58}')
        print('  ─' * 30)
        if user.error_message:
            print(f'  Error loading profile: {user.error_message}')
        else:
            print(f'  {"Name":<12}: {user.name}')
            print(f'  {"Username":<12}: {user.username}')
            print(f'  {"Email":<12}: {user.email}')
            print(f'  {"Role":<12}: {user.role.capitalize()}')
        print('  ─' * 30)
        pause()