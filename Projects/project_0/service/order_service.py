from DAO.order_dao import OrderDAO
from models.order_model import (
    DirectBuyRequest, DirectBuyResponse,
    ViewOrdersResponse, ViewOrderDetailsResponse,
    CancelOrderRequest, CancelOrderResponse
)

class OrderService:
    def __init__(self):
        self.order_dao = OrderDAO()

    def direct_buy(self, request: DirectBuyRequest) -> DirectBuyResponse:
        try:
            if request.quantity is None or request.quantity <= 0:
                raise ValueError('Quantity must be greater than zero.')
            if request.user_id is None or request.product_id is None:
                raise ValueError('user_id and product_id are required.')
        except ValueError as e:
            return DirectBuyResponse(success=False, error_message=str(e))
        return self.order_dao.direct_buy(request)

    def get_orders(self, user_id: int) -> ViewOrdersResponse:
        return self.order_dao.get_orders(user_id)

    def get_order_details(self, user_id: int, order_id: int) -> ViewOrderDetailsResponse:
        if not order_id or not user_id:
            return ViewOrderDetailsResponse(order=None, items=[], error_message='Invalid order_id or user_id.')
        return self.order_dao.get_order_details(user_id, order_id)

    def cancel_order(self, request: CancelOrderRequest) -> CancelOrderResponse:
        if not request.order_id:
            return CancelOrderResponse(success=False, error_message='order_id is required.')
        return self.order_dao.cancel_order(request)

