"""
Role-Based Access Control and Admin tests.
"""


def test_admin_get_users(client):
    """Test getting users list from admin controller."""
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_admin_create_user(client):
    """Test creating a user via admin controller."""
    payload = {
        "username": "admin_test_user",
        "password": "Password123!",
        "email": "admintest@example.com",
        "phone_no": "1234567890"
    }
    response = client.post("/admin/users", json=payload)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "user" in json_data
    assert json_data["user"]["username"] == "admin_test_user"
