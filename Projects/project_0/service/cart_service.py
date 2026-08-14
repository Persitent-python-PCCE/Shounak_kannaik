from DAO.cart_dao import CartDAO
from models.cart_model import AddToCartRequest, AddToCartResponse

class CartService:
    def __init__(self):
        self.cart_dao = CartDAO()

    def add_to_cart(self, request: AddToCartRequest) -> AddToCartResponse:
        try:
            if request.quantity is None or request.quantity <= 0:
                raise ValueError('Quantity must be greater than zero.')
            if request.user_id is None or request.product_id is None:
                raise ValueError('user_id and product_id are required.')
        except ValueError as e:
            return AddToCartResponse(success=False, error_message=str(e))
        return self.cart_dao.add_to_cart(request)
