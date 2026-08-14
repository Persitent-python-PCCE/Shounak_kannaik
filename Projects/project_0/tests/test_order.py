import unittest
from unittest.mock import MagicMock
from service.order_service import OrderService
from models.order_model import (
    DirectBuyRequest, DirectBuyResponse,
    CancelOrderRequest, CancelOrderResponse,
    UpdateOrderStatusRequest, UpdateOrderStatusResponse
)

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.order_service = OrderService()
        self.order_service.order_dao = MagicMock()

    def test_direct_buy_success(self):
        # Arrange
        req = DirectBuyRequest(user_id=1, product_id=10, quantity=1)
        mock_res = DirectBuyResponse(success=True, error_message=None, order_id=100)
        self.order_service.order_dao.direct_buy.return_value = mock_res
        
        # Act
        res = self.order_service.direct_buy(req)

        # Assert
        self.assertTrue(res.success)
        self.assertEqual(res.order_id, 100)
        self.order_service.order_dao.direct_buy.assert_called_once_with(req)

    def test_direct_buy_invalid_quantity(self):
        # Arrange
        req = DirectBuyRequest(user_id=1, product_id=10, quantity=0)
        
        # Act
        res = self.order_service.direct_buy(req)

        # Assert
        self.assertFalse(res.success)
        self.assertEqual(res.error_message, 'Quantity must be greater than zero.')
        self.order_service.order_dao.direct_buy.assert_not_called()

    def test_update_order_status_invalid_status(self):
        # Arrange
        req = UpdateOrderStatusRequest(order_id=100, status='unknown_status')
        
        # Act
        res = self.order_service.update_order_status(req)

        # Assert
        self.assertFalse(res.success)
        self.assertIn("Invalid status", res.error_message)
        self.order_service.order_dao.update_order_status.assert_not_called()

    def test_cancel_order_missing_id(self):
        # Arrange
        req = CancelOrderRequest(user_id=1, order_id=None)
        
        # Act
        res = self.order_service.cancel_order(req)

        # Assert
        self.assertFalse(res.success)
        self.assertEqual(res.error_message, 'order_id is required.')
        self.order_service.order_dao.cancel_order.assert_not_called()

if __name__ == '__main__':
    unittest.main()
