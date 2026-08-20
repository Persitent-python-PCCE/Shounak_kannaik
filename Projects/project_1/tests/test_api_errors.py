"""
API error tests.
"""


def test_api_404_not_found(client):
    """Test accessing non-existent route returns 404."""
    response = client.get("/non_existent_route")
    assert response.status_code == 404
