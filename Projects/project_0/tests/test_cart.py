import unittest
from unittest.mock import MagicMock
from service.cart_service import CartService
from models.cart_model import (
    AddToCartRequest, AddToCartResponse,
    UpdateCartItemRequest, UpdateCartItemResponse
)

class TestCartService(unittest.TestCase):
    def setUp(self):
        self.cart_service = CartService()
        self.cart_service.cart_dao = MagicMock()

    def test_add_to_cart_success(self):
        # Arrange
        req = AddToCartRequest(user_id=1, product_id=10, quantity=2)
        mock_res = AddToCartResponse(success=True, error_message=None)
        self.cart_service.cart_dao.add_to_cart.return_value = mock_res
        
        # Act
        res = self.cart_service.add_to_cart(req)

        # Assert
        self.assertTrue(res.success)
        self.cart_service.cart_dao.add_to_cart.assert_called_once_with(req)

    def test_add_to_cart_invalid_quantity(self):
        # Arrange
        req = AddToCartRequest(user_id=1, product_id=10, quantity=0)
        
        # Act
        res = self.cart_service.add_to_cart(req)

        # Assert
        self.assertFalse(res.success)
        self.assertEqual(res.error_message, 'Quantity must be greater than zero.')
        self.cart_service.cart_dao.add_to_cart.assert_not_called()

    def test_update_cart_quantity_zero(self):
        # Arrange
        req = UpdateCartItemRequest(user_id=1, product_id=10, new_quantity=0)
        mock_res = UpdateCartItemResponse(success=True, error_message=None) # if qty <= 0, it removes the item (which returns success=True)
        self.cart_service.cart_dao.update_cart_item.return_value = mock_res
        
        # Act
        res = self.cart_service.update_cart_item(req)

        # Assert
        self.assertFalse(res.success)
        self.assertEqual(res.error_message, 'Quantity must be greater than zero.')
        self.cart_service.cart_dao.update_cart_item.assert_not_called()

if __name__ == '__main__':
    unittest.main()
