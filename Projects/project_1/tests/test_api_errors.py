

def test_api_404_not_found(client):
    response = client.get("/non_existent_route")
    assert response.status_code == 404
