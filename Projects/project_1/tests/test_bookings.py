"""
Booking tests.
"""


def test_get_bookings(client):
    """Test getting bookings list."""
    response = client.get("/bookings/")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_booking(client):
    """Test creating a booking."""
    response = client.post("/bookings/", json={"schedule_id": 1, "seats": [101]})
    assert response.status_code == 201
    assert "booking" in response.get_json()
