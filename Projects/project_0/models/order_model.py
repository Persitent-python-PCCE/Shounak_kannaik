class DirectBuyRequest:
    def __init__(self, user_id: int, product_id: int, quantity: int):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

class DirectBuyResponse:
    def __init__(self, success: bool, error_message: str,
                 order_id: int = None, total_amount: float = None,
                 order_date=None, status: str = None,
                 product_id: int = None, quantity: int = None):
        self.success = success
        self.error_message = error_message
        self.order_id = order_id
        self.total_amount = total_amount
        self.order_date = order_date
        self.status = status
        self.product_id = product_id
        self.quantity = quantity
