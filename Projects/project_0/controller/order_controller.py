from service.order_service import OrderService
from models.order_model import DirectBuyRequest

class OrderController:
    def __init__(self):
        self.order_service = OrderService()

    def direct_buy(self, user_id: int, product_id: int, quantity: int):
        request = DirectBuyRequest(user_id=user_id, product_id=product_id, quantity=quantity)
        response = self.order_service.direct_buy(request)
        if response.success:
            print(f"""
------- Order Placed Successfully! -------
Order ID    : {response.order_id}
Status      : {response.status}
Quantity    : {response.quantity}
Total Price : {response.total_amount}
Order Date  : {response.order_date}
------------------------------------------""")
        else:
            print(f'Error: {response.error_message}')
