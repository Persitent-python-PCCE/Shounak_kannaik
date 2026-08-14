class CartModel:
    def __init__(self, user_id: int, status: str = "active", cart_id: int = None):
        self.cart_id = cart_id
        self.user_id = user_id
        self.status = status
    

class CartItems:
    def __init__(self, cart_id: int, product_id: int, quantity: int, cart_item_id = None):
        self.cart_item_id = cart_item_id
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity