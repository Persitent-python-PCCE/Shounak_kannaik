import unittest
from unittest.mock import MagicMock
from service.user_service import UserService
from models.user_models import UserloginRequest, UserLoginResponse

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()
        # Mock the DAO layer
        self.user_service.user_dao = MagicMock()

    def test_login_success(self):
        # Arrange
        req = UserloginRequest(username='testuser', password='password123')
        mock_response = UserLoginResponse(
            login_status=1, user_id=1, username='testuser', role='customer', error_message=None
        )
        self.user_service.user_dao.user_login.return_value = mock_response

        # Act
        res = self.user_service.user_login(req)

        # Assert
        self.assertEqual(res.login_status, 1)
        self.assertEqual(res.username, 'testuser')
        self.assertEqual(res.role, 'customer')
        self.assertIsNone(res.error_message)
        self.user_service.user_dao.user_login.assert_called_once_with(user=req)

    def test_login_invalid_password(self):
        # Arrange
        req = UserloginRequest(username='testuser', password='wrongpassword')
        mock_response = UserLoginResponse(
            login_status=0, user_id=None, username=None, role=None, error_message='Invalid username or password'
        )
        self.user_service.user_dao.user_login.return_value = mock_response

        # Act
        res = self.user_service.user_login(req)

        # Assert
        self.assertEqual(res.login_status, 0)
        self.assertEqual(res.error_message, 'Invalid username or password')
        self.user_service.user_dao.user_login.assert_called_once_with(user=req)

    def test_login_empty_credentials(self):
        # Arrange
        req = UserloginRequest(username='', password='')
        # Service should catch this before calling DAO
        
        # Act
        res = self.user_service.user_login(req)

        # Assert
        self.assertIsNone(res.login_status)
        self.assertEqual(res.error_message, "username cant be empty")
        self.user_service.user_dao.user_login.assert_not_called()

if __name__ == '__main__':
    unittest.main()
