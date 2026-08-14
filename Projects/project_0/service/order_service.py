from DAO.order_dao import OrderDAO
from models.order_model import DirectBuyRequest, DirectBuyResponse

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
