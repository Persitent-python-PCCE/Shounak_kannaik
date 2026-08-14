from config.database import get_connection
from mysql.connector import Error
from models.user_models import CreateUserRequest, CreateUserResponse, UserloginRequest, UserLoginResponse
from models.user_models import ShowAllUsersResponse
from models.user_models import SearchUserRequest, SearchUserResponse
from models.user_models import UpdateUserRequest, UpdateUserResponse
from models.user_models import DeleteUserRequest, DeleteUserResponse
class UserDAO:
    def __init__(self):
        self.con = get_connection()
        
    def create_user(self, user: CreateUserRequest) -> CreateUserResponse: 
        cursor= self.con.cursor()
        response_obj = CreateUserResponse(None, None)
        try:
            query = "INSERT INTO users(username, name, email, password, role) VALUES(%s, %s, %s, %s, %s)"
            values = (user.username, user.name, user.email, user.password, user.role)
            cursor.execute(query, values)
            self.con.commit()
            
            response_obj.user_id =cursor.lastrowid 
        except Error as e:
            response_obj.error_message = e.msg
            
        cursor.close()
        return response_obj
    
    
    def user_login(self, user: UserloginRequest) -> UserLoginResponse:
        cursor= self.con.cursor()
        response_obj = UserLoginResponse(None, None, None, None, None)
        try:
            args = (user.username,user.password, None, None,None, None)
            result = cursor.callproc("user_login", args)

            login_success = result[2]
            user_id = result[3]
            username = result[4]
            role = result[5]
            

            if login_success:
                response_obj.login_status = login_success
                response_obj.user_id = user_id
                response_obj.username = username
                response_obj.role = role
            else:
                response_obj.login_status = 0
                response_obj.error_message = ("login unsuccessful. check username and password")

        except Error as e:
            response_obj.error_message = e.msg
            
        cursor.close()
        return response_obj
    
    def show_all_users(self) -> list[ShowAllUsersResponse]:
        cursor = self.con.cursor()
        try:
            query = "SELECT user_id, username, name, email, role FROM users;"
            cursor.execute(query)
            query_response = cursor.fetchall()
            response = []

            for user in query_response:
                obj = ShowAllUsersResponse(
                    user_id=user[0],
                    username=user[1],
                    name=user[2],
                    email=user[3],
                    role=user[4]
                )
                response.append(obj)
            return response
        except Error as e:
            raise e
        finally:
            cursor.close()
    
    def search_user(self, user: SearchUserRequest)->SearchUserResponse:
        cursor = self.con.cursor()
        response_obj = SearchUserResponse(None, None, None, None, None, None)
        try:
            query = "SELECT user_id, username, name, email, role FROM users WHERE username = %s;"
            values = (user.username,)
            cursor.execute(query, values)
            
            query_response =cursor.fetchone()
            if query_response is not None:
                response_obj.user_id = query_response[0]
                response_obj.username = query_response[1]
                response_obj.name = query_response[2]
                response_obj.email = query_response[3]
                response_obj.role = query_response[4]
            else:
                response_obj.error_message = "User not found. Check Username"
        except Error as e:
            response_obj.error_message = e.msg

        cursor.close()
        return response_obj
            
    def update_user(self, user: UpdateUserRequest)->UpdateUserResponse:
        cursor = self.con.cursor()
        response_obj = UpdateUserResponse(None, None)
        try:
            query = "SELECT user_id, username,name, email, role, password FROM users WHERE user_id = %s;"
            values = (user.user_id,)
            cursor.execute(query, values)
            
            curent_details = cursor.fetchone()
            if curent_details is not None:
                current_user_id = curent_details[0]
                current_username = curent_details[1]
                current_name = curent_details[2]
                current_email = curent_details[3]
                current_role = curent_details[4]
                current_password = curent_details[5]
            else:
                raise ValueError("User not found. Check Username")
            new_name = user.name if user.name != "" else current_name
            new_username = user.username if user.username != "" else current_username
            new_password = user.password if user.password != "" else current_password
            new_email = user.email if user.email != "" else current_email
            new_role = user.role if user.role != "" else current_role
            
            query = "UPDATE users SET name = %s, username = %s, password= %s ,email = %s, role = %s WHERE user_id = %s"
            values = (new_name,new_username,new_password,new_email,new_role,current_user_id)
            cursor.execute(query, values)
            self.con.commit()
            response_obj.affected_rows = cursor.rowcount
        except ValueError as e:
            response_obj.error_message = str(e)
        except Error as e:
            response_obj.error_message = e.msg
            
        cursor.close()
        return response_obj

    def delete_user(self, user: DeleteUserRequest) -> DeleteUserResponse:
        cursor = self.con.cursor()
        response_obj = DeleteUserResponse(None, None)
        try:
            query = "DELETE FROM users WHERE user_id = %s"
            values = (user.user_id,)
            cursor.execute(query, values)
            self.con.commit()
            if cursor.rowcount == 0:
                response_obj.error_message = f"No user found with user_id {user.user_id}"
            else:
                response_obj.affected_rows = cursor.rowcount
        except Error as e:
            response_obj.error_message = e.msg
        finally:
            cursor.close()
        return response_obj