"""
Booking tests.
"""


def test_get_bookings(client, customer_headers):
    """Test getting bookings list for authenticated user."""
    response = client.get("/bookings/", headers=customer_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_bookings_unauthenticated(client):
    """Test getting bookings without auth fails with 401."""
    response = client.get("/bookings/")
    assert response.status_code == 401
