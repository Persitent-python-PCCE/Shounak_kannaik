from config.database import get_connection
from mysql.connector import Error
from models.order_model import DirectBuyRequest, DirectBuyResponse

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
