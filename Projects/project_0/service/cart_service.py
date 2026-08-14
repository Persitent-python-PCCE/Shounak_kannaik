from DAO.cart_dao import CartDAO
from models.cart_model import (
    AddToCartRequest, AddToCartResponse,
    ViewCartResponse,
    UpdateCartItemRequest, UpdateCartItemResponse,
    RemoveCartItemRequest, RemoveCartItemResponse,
    CheckoutCartRequest, CheckoutCartResponse
)

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

    def view_cart(self, user_id: int) -> ViewCartResponse:
        return self.cart_dao.view_cart(user_id)

    def update_cart_item(self, request: UpdateCartItemRequest) -> UpdateCartItemResponse:
        try:
            if request.new_quantity is None or request.new_quantity <= 0:
                raise ValueError('Quantity must be greater than zero.')
        except ValueError as e:
            return UpdateCartItemResponse(success=False, error_message=str(e))
        return self.cart_dao.update_cart_item(request)

    def remove_cart_item(self, request: RemoveCartItemRequest) -> RemoveCartItemResponse:
        return self.cart_dao.remove_cart_item(request)

    def checkout_cart(self, request: CheckoutCartRequest) -> CheckoutCartResponse:
        if request.user_id is None:
            return CheckoutCartResponse(success=False, error_message='user_id is required.')
        return self.cart_dao.checkout_cart(request)

