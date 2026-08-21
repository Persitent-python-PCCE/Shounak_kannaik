"""
Role-Based Access Control and Admin Route tests.
"""


def test_admin_route_unauthenticated(client):
    """Unauthenticated requests to admin routes must return 401."""
    response = client.get("/admin/users")
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Unauthorized"


def test_admin_route_forbidden_for_customer(client, customer_headers):
    """Customer role accessing admin route must return 403 Forbidden."""
    response = client.get("/admin/users", headers=customer_headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "Forbiden"


def test_admin_route_allowed_for_admin(client, admin_headers):
    """Admin role accessing admin route must return 200 OK."""
    response = client.get("/admin/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_admin_create_venue(client, admin_headers):
    """Admin can create new venues."""
    payload = {
        "name": "Grand Arena",
        "city": "Metropolis",
        "state": "NY",
        "country": "USA",
        "address": "100 Stadium Way",
        "capacity": 50000
    }
    response = client.post("/admin/venues", json=payload, headers=admin_headers)
    assert response.status_code == 201


def test_customer_cannot_create_venue(client, customer_headers):
    """Customer cannot create venues (returns 403)."""
    payload = {
        "name": "Rogue Arena",
        "city": "Metropolis",
        "state": "NY",
        "country": "USA",
        "address": "100 Stadium Way",
        "capacity": 50000
    }
    response = client.post("/admin/venues", json=payload, headers=customer_headers)
    assert response.status_code == 403
