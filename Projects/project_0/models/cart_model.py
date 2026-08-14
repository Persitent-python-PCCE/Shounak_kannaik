class AddToCartRequest:
    def __init__(self, user_id: int, product_id: int, quantity: int):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

class AddToCartResponse:
    def __init__(self, success: bool, error_message: str):
        self.success = success
        self.error_message = error_message


# --- View Cart ---
class CartItemModel:
    def __init__(self, product_id: int, product_name: str, quantity: int,
                 unit_price: float, subtotal: float):
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.subtotal = subtotal

class ViewCartResponse:
    def __init__(self, items: list, total_amount: float, error_message: str = None):
        self.items = items                  # list of CartItemModel
        self.total_amount = total_amount
        self.error_message = error_message


# --- Update Cart Item ---
class UpdateCartItemRequest:
    def __init__(self, user_id: int, product_id: int, new_quantity: int):
        self.user_id = user_id
        self.product_id = product_id
        self.new_quantity = new_quantity

class UpdateCartItemResponse:
    def __init__(self, success: bool, error_message: str = None):
        self.success = success
        self.error_message = error_message


# --- Remove Cart Item ---
class RemoveCartItemRequest:
    def __init__(self, user_id: int, product_id: int):
        self.user_id = user_id
        self.product_id = product_id

class RemoveCartItemResponse:
    def __init__(self, success: bool, error_message: str = None):
        self.success = success
        self.error_message = error_message


# --- Checkout Cart ---
class CheckoutCartRequest:
    def __init__(self, user_id: int):
        self.user_id = user_id

class CheckoutCartResponse:
    def __init__(self, success: bool, error_message: str = None,
                 order_id: int = None, total_amount: float = None,
                 order_date=None, status: str = None):
        self.success = success
        self.error_message = error_message
        self.order_id = order_id
        self.total_amount = total_amount
        self.order_date = order_date
        self.status = status
