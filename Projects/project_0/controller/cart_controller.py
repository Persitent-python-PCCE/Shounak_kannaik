from service.cart_service import CartService
from models.cart_model import AddToCartRequest

class CartController:
    def __init__(self):
        self.cart_service = CartService()

    def add_to_cart(self, user_id: int, product_id: int, quantity: int):
        request = AddToCartRequest(user_id=user_id, product_id=product_id, quantity=quantity)
        response = self.cart_service.add_to_cart(request)
        if response.success:
            print('Product added to cart successfully!')
        else:
            print(f'Error: {response.error_message}')
