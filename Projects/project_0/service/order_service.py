from DAO.order_dao import OrderDAO
from models.order_model import (
    DirectBuyRequest, DirectBuyResponse,
    ViewOrdersResponse, ViewOrderDetailsResponse,
    CancelOrderRequest, CancelOrderResponse,
    ViewAllOrdersResponse, UpdateOrderStatusRequest,
    UpdateOrderStatusResponse, CancelOrderByIdRequest
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

    # --- All Orders Management ---
    
    def get_all_orders(self) -> ViewAllOrdersResponse:
        return self.order_dao.get_all_orders()

    def search_order(self, order_id: int) -> ViewAllOrdersResponse:
        if not order_id:
            return ViewAllOrdersResponse(orders=[], error_message='order_id is required.')
        return self.order_dao.search_order(order_id)

    def get_admin_order_details(self, order_id: int) -> ViewOrderDetailsResponse:
        if not order_id:
            return ViewOrderDetailsResponse(order=None, items=[], error_message='order_id is required.')
        return self.order_dao.get_admin_order_details(order_id)

    def update_order_status(self, request: UpdateOrderStatusRequest) -> UpdateOrderStatusResponse:
        if not request.order_id or not request.status:
            return UpdateOrderStatusResponse(success=False, error_message='order_id and status are required.')
        valid_statuses = ['placed', 'processing', 'shipped', 'completed', 'cancelled']
        if request.status.lower() not in valid_statuses:
            return UpdateOrderStatusResponse(success=False, error_message=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return self.order_dao.update_order_status(request)

    def admin_cancel_order(self, request: CancelOrderByIdRequest) -> CancelOrderResponse:
        if not request.order_id:
            return CancelOrderResponse(success=False, error_message='order_id is required.')
        return self.order_dao.admin_cancel_order(request)

