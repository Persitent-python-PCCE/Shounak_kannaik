from config.database import get_connection
from mysql.connector import Error
from models.cart_model import (
    AddToCartRequest, AddToCartResponse,
    CartItemModel, ViewCartResponse,
    UpdateCartItemRequest, UpdateCartItemResponse,
    RemoveCartItemRequest, RemoveCartItemResponse,
    CheckoutCartRequest, CheckoutCartResponse
)

class CartDAO:
    def __init__(self):
        self.con = get_connection()

    def add_to_cart(self, request: AddToCartRequest) -> AddToCartResponse:
        cursor = self.con.cursor()
        response_obj = AddToCartResponse(success=False, error_message=None)
        try:
            args = (request.user_id, request.product_id, request.quantity, False)
            result = cursor.callproc('sp_add_product_to_cart', args)
            op_success = result[3]
            if op_success:
                response_obj.success = True
            else:
                response_obj.error_message = 'Could not add to cart. Product may be out of stock or invalid.'
        except Error as e:
            response_obj.error_message = e.msg
        cursor.close()
        return response_obj

    def view_cart(self, user_id: int) -> ViewCartResponse:
        cursor = self.con.cursor()
        try:
            query = """
                SELECT p.product_id, p.name, ci.quantity, p.unit_price,
                       (ci.quantity * p.unit_price) AS subtotal
                FROM carts c
                JOIN cart_items ci ON ci.cart_id = c.cart_id
                JOIN products p ON p.product_id = ci.product_id
                WHERE c.user_id = %s AND c.status = 'active'
                ORDER BY p.name;
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            items = []
            total = 0.0
            for row in rows:
                item = CartItemModel(
                    product_id=row[0],
                    product_name=row[1],
                    quantity=row[2],
                    unit_price=float(row[3]),
                    subtotal=float(row[4])
                )
                total += item.subtotal
                items.append(item)
            return ViewCartResponse(items=items, total_amount=round(total, 2))
        except Error as e:
            return ViewCartResponse(items=[], total_amount=0.0, error_message=e.msg)
        finally:
            cursor.close()

    def update_cart_item(self, request: UpdateCartItemRequest) -> UpdateCartItemResponse:
        cursor = self.con.cursor()
        try:
            query = """
                UPDATE cart_items ci
                JOIN carts c ON c.cart_id = ci.cart_id
                SET ci.quantity = %s
                WHERE c.user_id = %s AND ci.product_id = %s AND c.status = 'active';
            """
            cursor.execute(query, (request.new_quantity, request.user_id, request.product_id))
            self.con.commit()
            if cursor.rowcount == 0:
                return UpdateCartItemResponse(success=False, error_message='Item not found in cart.')
            return UpdateCartItemResponse(success=True)
        except Error as e:
            self.con.rollback()
            return UpdateCartItemResponse(success=False, error_message=e.msg)
        finally:
            cursor.close()

    def remove_cart_item(self, request: RemoveCartItemRequest) -> RemoveCartItemResponse:
        cursor = self.con.cursor()
        try:
            query = """
                DELETE ci FROM cart_items ci
                JOIN carts c ON c.cart_id = ci.cart_id
                WHERE c.user_id = %s AND ci.product_id = %s AND c.status = 'active';
            """
            cursor.execute(query, (request.user_id, request.product_id))
            self.con.commit()
            if cursor.rowcount == 0:
                return RemoveCartItemResponse(success=False, error_message='Item not found in cart.')
            return RemoveCartItemResponse(success=True)
        except Error as e:
            self.con.rollback()
            return RemoveCartItemResponse(success=False, error_message=e.msg)
        finally:
            cursor.close()

    def checkout_cart(self, request: CheckoutCartRequest) -> CheckoutCartResponse:
        cursor = self.con.cursor()
        response_obj = CheckoutCartResponse(success=False)
        try:
            args = (request.user_id, None, None, False)
            result = cursor.callproc('sp_checkout_cart', args)

            op_order_id     = result[1]
            op_total_amount = result[2]
            op_success      = result[3]

            if op_success:
                response_obj.success = True
                response_obj.order_id = op_order_id
                response_obj.total_amount = float(op_total_amount) if op_total_amount else None
                # Fetch the result set (order_id, status, total_amount, order_date)
                for res in cursor.stored_results():
                    row = res.fetchone()
                    if row:
                        response_obj.order_id     = row[0]
                        response_obj.status       = row[1]
                        response_obj.total_amount = float(row[2])
                        response_obj.order_date   = row[3]
            else:
                response_obj.error_message = 'Checkout failed. Cart may be empty, inactive, or a product is out of stock.'
        except Error as e:
            response_obj.error_message = e.msg
        finally:
            cursor.close()
        return response_obj
