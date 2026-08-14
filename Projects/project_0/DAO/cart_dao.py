from config.database import get_connection
from mysql.connector import Error
from models.cart_model import AddToCartRequest, AddToCartResponse

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
