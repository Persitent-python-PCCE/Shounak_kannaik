from config.database import get_connection
from mysql.connector import Error
from models.category_model import (
    CreateCategoryRequest, CreateCategoryResponse,
    ShowAllCategoriesResponse,
    SearchCategoryRequest, SearchCategoryResponse,
    UpdateCategoryRequest, UpdateCategoryResponse,
    DeleteCategoryRequest, DeleteCategoryResponse,
    ViewCategoryProductsRequest
)

class CategoryDAO:
    def __init__(self):
        self.con = get_connection()

    def create_category(self, category: CreateCategoryRequest) -> CreateCategoryResponse:
        cursor = self.con.cursor()
        response_obj = CreateCategoryResponse(None, None)
        try:
            query = "INSERT INTO categories(name) VALUES(%s)"
            values = (category.name,)
            cursor.execute(query, values)
            self.con.commit()
            response_obj.category_id = cursor.lastrowid
        except Error as e:
            response_obj.error_message = e.msg
        cursor.close()
        return response_obj

    def show_all_categories(self) -> list:
        cursor = self.con.cursor()
        try:
            query = "SELECT category_id, name FROM categories;"
            cursor.execute(query)
            query_response = cursor.fetchall()
            response = []
            for row in query_response:
                obj = ShowAllCategoriesResponse(
                    category_id=row[0],
                    name=row[1]
                )
                response.append(obj)
            return response
        except Error as e:
            raise e
        cursor.close()

    def search_category(self, category: SearchCategoryRequest) -> SearchCategoryResponse:
        cursor = self.con.cursor()
        response_obj = SearchCategoryResponse(None, None, None)
        try:
            query = "SELECT category_id, name FROM categories WHERE name LIKE %s;"
            values = (category.name)
            cursor.execute(query, values)
            query_response = cursor.fetchone()
            if query_response is not None:
                response_obj.category_id = query_response[0]
                response_obj.name = query_response[1]
            else:
                response_obj.error_message = f"No category found with name '{category.name}'"
        except Error as e:
            response_obj.error_message = e.msg
        cursor.close()
        return response_obj

    def update_category(self, category: UpdateCategoryRequest) -> UpdateCategoryResponse:
        cursor = self.con.cursor()
        response_obj = UpdateCategoryResponse(None, None)
        try:
            check_query = "SELECT category_id, name FROM categories WHERE category_id = %s;"
            cursor.execute(check_query, (category.category_id,))
            current = cursor.fetchone()
            if current is None:
                raise ValueError(f"No category found with category_id {category.category_id}")

            new_name = category.name if category.name.strip() != "" else current[1]

            query = "UPDATE categories SET name = %s WHERE category_id = %s"
            values = (new_name, category.category_id)
            cursor.execute(query, values)
            self.con.commit()
            response_obj.affected_rows = cursor.rowcount
        except ValueError as e:
            response_obj.error_message = str(e)
        except Error as e:
            response_obj.error_message = e.msg
        finally:
            cursor.close()
        return response_obj

    def delete_category(self, category: DeleteCategoryRequest) -> DeleteCategoryResponse:
        cursor = self.con.cursor()
        response_obj = DeleteCategoryResponse(None, None)
        try:
            query = "DELETE FROM categories WHERE category_id = %s"
            values = (category.category_id,)
            cursor.execute(query, values)
            self.con.commit()
            if cursor.rowcount == 0:
                response_obj.error_message = f"No category found with category_id {category.category_id}"
            else:
                response_obj.affected_rows = cursor.rowcount
        except Error as e:
            response_obj.error_message = e.msg
        finally:
            cursor.close()
        return response_obj

    def view_category_products(self, category: ViewCategoryProductsRequest) -> list:
        cursor = self.con.cursor()
        try:
            # Verify category exists
            check_query = "SELECT name FROM categories WHERE category_id = %s;"
            cursor.execute(check_query, (category.category_id,))
            cat = cursor.fetchone()
            if cat is None:
                raise ValueError(f"No category found with category_id {category.category_id}")

            query = """
                SELECT p.product_id, p.name, p.description, p.unit_price, p.stock_available
                FROM products p
                WHERE p.category_id = %s
                ORDER BY p.product_id;
            """
            cursor.execute(query, (category.category_id,))
            rows = cursor.fetchall()
            return rows
        except (Error, ValueError) as e:
            raise e
        finally:
            cursor.close()
