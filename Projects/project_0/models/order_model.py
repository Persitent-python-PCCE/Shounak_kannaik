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


# --- View All Orders (summary list) ---
class OrderSummaryModel:
    def __init__(self, order_id: int, order_date, status: str, total_amount: float):
        self.order_id = order_id
        self.order_date = order_date
        self.status = status
        self.total_amount = total_amount

class ViewOrdersResponse:
    def __init__(self, orders: list, error_message: str = None):
        self.orders = orders          # list of OrderSummaryModel
        self.error_message = error_message


# --- View Order Details ---
class OrderItemModel:
    def __init__(self, product_id: int, product_name: str,
                 quantity: int, unit_price: float, subtotal: float):
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.subtotal = subtotal

class ViewOrderDetailsResponse:
    def __init__(self, order: OrderSummaryModel, items: list, error_message: str = None):
        self.order = order            # OrderSummaryModel
        self.items = items            # list of OrderItemModel
        self.error_message = error_message


# --- Cancel Order ---
class CancelOrderRequest:
    def __init__(self, user_id: int, order_id: int):
        self.user_id = user_id
        self.order_id = order_id

class CancelOrderResponse:
    def __init__(self, success: bool, error_message: str = None):
        self.success = success
        self.error_message = error_message

