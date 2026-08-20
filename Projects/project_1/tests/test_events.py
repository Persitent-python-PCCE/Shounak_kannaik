"""
Event catalog tests.
"""


def test_get_events(client):
    """Test getting events list."""
    response = client.get("/events/")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
