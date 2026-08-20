"""
Authentication tests.
"""


def test_api_login(client):
    """Test login endpoint."""
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "secret"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert "message" in json_data
