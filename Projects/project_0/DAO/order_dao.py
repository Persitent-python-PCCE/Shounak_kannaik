from config.database import get_connection
from mysql.connector import Error
from models.order_model import (
    DirectBuyRequest, DirectBuyResponse,
    OrderSummaryModel, ViewOrdersResponse,
    OrderItemModel, ViewOrderDetailsResponse,
    CancelOrderRequest, CancelOrderResponse
)

class OrderDAO:
    def __init__(self):
        self.con = get_connection()

    def direct_buy(self, request: DirectBuyRequest) -> DirectBuyResponse:
        cursor = self.con.cursor()
        response_obj = DirectBuyResponse(success=False, error_message=None)
        try:
            args = (request.user_id, request.product_id, request.quantity, None, False)
            result = cursor.callproc('sp_buy_product_directly', args)

            op_order_id = result[3]
            op_success = result[4]

            if op_success:
                response_obj.success = True
                response_obj.order_id = op_order_id

                # Fetch the result set returned by the SP (order details)
                for res in cursor.stored_results():
                    row = res.fetchone()
                    if row:
                        # Columns: order_id, user_id, order_date, status, total_amount,
                        #          order_item_id, product_id, quantity, unit_price
                        response_obj.order_id = row[0]
                        response_obj.order_date = row[2]
                        response_obj.status = row[3]
                        response_obj.total_amount = row[4]
                        response_obj.product_id = row[6]
                        response_obj.quantity = row[7]
            else:
                response_obj.error_message = 'Purchase failed. Product may be out of stock or invalid.'
        except Error as e:
            response_obj.error_message = e.msg
        cursor.close()
        return response_obj

    def get_orders(self, user_id: int) -> ViewOrdersResponse:
        cursor = self.con.cursor()
        try:
            query = """
                SELECT order_id, order_date, status, total_amount
                FROM orders
                WHERE user_id = %s
                ORDER BY order_date DESC;
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            orders = [
                OrderSummaryModel(
                    order_id=row[0],
                    order_date=row[1],
                    status=row[2],
                    total_amount=float(row[3])
                )
                for row in rows
            ]
            return ViewOrdersResponse(orders=orders)
        except Error as e:
            return ViewOrdersResponse(orders=[], error_message=e.msg)
        finally:
            cursor.close()

    def get_order_details(self, user_id: int, order_id: int) -> ViewOrderDetailsResponse:
        cursor = self.con.cursor()
        try:
            # Fetch order summary
            cursor.execute(
                "SELECT order_id, order_date, status, total_amount FROM orders WHERE order_id = %s AND user_id = %s;",
                (order_id, user_id)
            )
            row = cursor.fetchone()
            if row is None:
                return ViewOrderDetailsResponse(order=None, items=[], error_message='Order not found.')
            order = OrderSummaryModel(order_id=row[0], order_date=row[1], status=row[2], total_amount=float(row[3]))

            # Fetch order items joined with product name
            cursor.execute("""
                SELECT oi.product_id, p.name, oi.quantity, oi.unit_price,
                       (oi.quantity * oi.unit_price) AS subtotal
                FROM order_items oi
                JOIN products p ON p.product_id = oi.product_id
                WHERE oi.order_id = %s
                ORDER BY p.name;
            """, (order_id,))
            item_rows = cursor.fetchall()
            items = [
                OrderItemModel(
                    product_id=r[0], product_name=r[1], quantity=r[2],
                    unit_price=float(r[3]), subtotal=float(r[4])
                )
                for r in item_rows
            ]
            return ViewOrderDetailsResponse(order=order, items=items)
        except Error as e:
            return ViewOrderDetailsResponse(order=None, items=[], error_message=e.msg)
        finally:
            cursor.close()

    def cancel_order(self, request: CancelOrderRequest) -> CancelOrderResponse:
        cursor = self.con.cursor()
        try:
            self.con.start_transaction()
            # Fetch order — verify it belongs to this user and get current status
            cursor.execute(
                "SELECT status FROM orders WHERE order_id = %s AND user_id = %s FOR UPDATE;",
                (request.order_id, request.user_id)
            )
            row = cursor.fetchone()
            if row is None:
                return CancelOrderResponse(success=False, error_message='Order not found.')

            current_status = row[0]
            if current_status == 'completed':
                return CancelOrderResponse(success=False, error_message='Cannot cancel a completed order.')
            if current_status == 'cancelled':
                return CancelOrderResponse(success=False, error_message='Order is already cancelled.')

            # Restore stock for all items in the order
            cursor.execute("""
                UPDATE products p
                JOIN order_items oi ON oi.product_id = p.product_id
                SET p.stock_available = p.stock_available + oi.quantity
                WHERE oi.order_id = %s;
            """, (request.order_id,))

            # Cancel the order
            cursor.execute(
                "UPDATE orders SET status = 'cancelled' WHERE order_id = %s;",
                (request.order_id,)
            )
            self.con.commit()
            return CancelOrderResponse(success=True)
        except Error as e:
            self.con.rollback()
            return CancelOrderResponse(success=False, error_message=e.msg)
        finally:
            cursor.close()

