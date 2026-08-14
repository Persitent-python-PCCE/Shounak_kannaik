import datetime
class OrderModel:
    def __init__(self, user_id: int, order_date: datetime, order_total: int, status: str, order_id=None):
        self.order_id = order_id
        self.user_id = user_id
        self.order_date = order_date
        self.order_total = order_total        
        self.status = status
    

class OrderItemsModel:
    def __init__(self, order_id: int, product_id: int, quantity: int, unit_price: float, order_item_id = None):
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price