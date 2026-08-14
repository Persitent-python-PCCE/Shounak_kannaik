from config.database import get_connection
from mysql.connector import Error
from models.product_model import (
    CreateProductRequest, CreateProductResponse,
    ShowAllProductsResponse,
    SearchProductRequest, SearchProductResponse,
    UpdateProductRequest, UpdateProductResponse,
    DeleteProductRequest, DeleteProductResponse
)

class ProductDAO:
    def __init__(self):
        self.con = get_connection()

    def create_product(self, product: CreateProductRequest) -> CreateProductResponse:
        cursor = self.con.cursor()
        response_obj = CreateProductResponse(None, None)
        try:
            query = "INSERT INTO products(category_id, name, description, unit_price, stock_available) VALUES(%s, %s, %s, %s, %s)"
            values = (product.category_id, product.name, product.description, product.unit_price, product.stock_available)
            cursor.execute(query, values)
            self.con.commit()
            response_obj.product_id = cursor.lastrowid
        except Error as e:
            response_obj.error_message = e.msg
        cursor.close()
        return response_obj

    def show_all_products(self) -> list:
        cursor = self.con.cursor()
        try:
            query = """SELECT p.product_id, c.name as 'category', p.name, p.description, p.unit_price, p.stock_available, p.created_at FROM products p 
                JOIN categories c ON p.category_id = c.category_id ORDER BY p.product_id;"""
            cursor.execute(query)
            query_response = cursor.fetchall()
            response = []
            for row in query_response:
                obj = ShowAllProductsResponse(
                    product_id=row[0],
                    category=row[1],
                    name=row[2],
                    description=row[3],
                    unit_price=row[4],
                    stock_available=row[5],
                    created_at=row[6]
                )
                response.append(obj)
            return response
        except Error as e:
            raise e
        cursor.close()

    def search_product(self, product: SearchProductRequest) -> list:
        cursor = self.con.cursor()
        try:
            query = """
                SELECT p.product_id, c.name, p.name, p.description, p.unit_price, p.stock_available, p.created_at
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
                WHERE p.name LIKE %s
                ORDER BY p.product_id;
            """
            values = (f"%{product.name}%",)
            cursor.execute(query, values)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                obj = SearchProductResponse(
                    product_id=row[0],
                    category=row[1],
                    name=row[2],
                    description=row[3],
                    unit_price=row[4],
                    stock_available=row[5],
                    created_at=row[6],
                    error_message=None
                )
                response.append(obj)
            return response
        except Error as e:
            raise e
        finally:
            cursor.close()

    def update_product(self, product: UpdateProductRequest) -> UpdateProductResponse:
        cursor = self.con.cursor()
        response_obj = UpdateProductResponse(None, None)
        try:
            # Fetch current product details
            query = "SELECT product_id, category_id, name, description, unit_price, stock_available FROM products WHERE product_id = %s;"
            cursor.execute(query, (product.product_id,))
            current = cursor.fetchone()
            if current is None:
                raise ValueError(f"No product found with product_id {product.product_id}")

            current_product_id = current[0]
            current_category_id = current[1]
            current_name = current[2]
            current_description = current[3]
            current_unit_price = current[4]
            current_stock_available = current[5]

            # Use new values if provided, otherwise keep current
            new_name = product.name if product.name.strip() != "" else current_name
            new_category_id = product.category_id if product.category_id != "" else current_category_id
            new_description = product.description if product.description.strip() != "" else current_description
            new_unit_price = float(product.unit_price) if product.unit_price.strip() != "" else current_unit_price
            new_stock = int(product.stock_available) if product.stock_available.strip() != "" else current_stock_available

            update_query = """
                UPDATE products
                SET category_id = %s, name = %s, description = %s, unit_price = %s, stock_available = %s
                WHERE product_id = %s
            """
            values = (new_category_id, new_name, new_description, new_unit_price, new_stock, current_product_id)
            cursor.execute(update_query, values)
            self.con.commit()
            response_obj.affected_rows = cursor.rowcount
        except ValueError as e:
            response_obj.error_message = str(e)
        except Error as e:
            response_obj.error_message = e.msg
        finally:
            cursor.close()
        return response_obj

    def delete_product(self, product: DeleteProductRequest) -> DeleteProductResponse:
        cursor = self.con.cursor()
        response_obj = DeleteProductResponse(None, None)
        try:
            query = "DELETE FROM products WHERE product_id = %s"
            values = (product.product_id,)
            cursor.execute(query, values)
            self.con.commit()
            if cursor.rowcount == 0:
                response_obj.error_message = f"No product found with product_id {product.product_id}"
            else:
                response_obj.affected_rows = cursor.rowcount
        except Error as e:
            response_obj.error_message = e.msg
        finally:
            cursor.close()
        return response_obj
