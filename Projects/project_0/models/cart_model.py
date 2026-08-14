class AddToCartRequest:
    def __init__(self, user_id: int, product_id: int, quantity: int):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

class AddToCartResponse:
    def __init__(self, success: bool, error_message: str):
        self.success = success
        self.error_message = error_message
