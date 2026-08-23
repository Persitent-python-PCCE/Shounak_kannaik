"""
Authentication tests.
"""

import io


def test_register_success(client):
    """Test registering a new user with valid document upload."""
    file_data = io.BytesIO(b"%PDF-1.4 dummy pdf document content")
    payload = {
        "username": "new_user",
        "email": "new@example.com",
        "password": "Password123!",
        "phone_no": "9876543210",
        "doc_type": "Aadhaar",
        "id_document": (file_data, "id_proof.pdf")
    }
    response = client.post("/auth/register", data=payload, content_type="multipart/form-data")
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "User created successfully"
    assert data["user"]["username"] == "new_user"
    assert data["user"]["role"] == "customer"  # Verify default role
    assert "document" in data
    assert data["document"]["doc_type"] == "Aadhaar"


def test_register_without_document_success(client):
    """Test registering a new user without document succeeds with 201."""
    payload = {
        "username": "no_doc_user",
        "email": "nodoc@example.com",
        "password": "Password123!",
        "phone_no": "9876543211"
    }
    response = client.post("/auth/register", data=payload, content_type="multipart/form-data")
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "User created successfully"
    assert data["user"]["username"] == "no_doc_user"
    assert "document" not in data or data["document"] is None


def test_register_invalid_file_extension(client):
    """Test registering with an invalid file extension returns 400."""
    file_data = io.BytesIO(b"malicious script contents")
    payload = {
        "username": "bad_ext_user",
        "email": "badext@example.com",
        "password": "Password123!",
        "phone_no": "9876543212",
        "id_document": (file_data, "exploit.exe")
    }
    response = client.post("/auth/register", data=payload, content_type="multipart/form-data")
    assert response.status_code == 400
    data = response.get_json()
    assert "File extension is not allowed" in data["error"]


def test_register_invalid_phone_number(client):
    """Test registering with a non-numeric phone number returns 400."""
    file_data = io.BytesIO(b"%PDF-1.4 dummy pdf document content")
    payload = {
        "username": "bad_phone_user",
        "email": "badphone@example.com",
        "password": "Password123!",
        "phone_no": "invalid_phone_text",
        "id_document": (file_data, "id_proof.pdf")
    }
    response = client.post("/auth/register", data=payload, content_type="multipart/form-data")
    assert response.status_code == 400
    data = response.get_json()
    assert "Invalid phone number format" in data["error"]


def test_login_success(client, customer_user):
    """Test successful login returns a valid JWT."""
    payload = {
        "username": "john_customer",
        "password": "Password123!"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert data["user"]["username"] == "john_customer"


def test_login_invalid_password(client, customer_user):
    """Test login with wrong password returns 401."""
    payload = {
        "username": "john_customer",
        "password": "WrongPassword!"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_login_missing_fields(client):
    """Test login with missing fields returns 400."""
    response = client.post("/auth/login", json={"username": "alone"})
    assert response.status_code == 400


def test_protected_route_missing_token(client):
    """Test accessing protected route without Authorization header returns 401."""
    response = client.get("/bookings/")
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Unauthorized"


def test_protected_route_malformed_header(client):
    """Test accessing protected route with malformed Authorization header returns 401."""
    response = client.get("/bookings/", headers={"Authorization": "InvalidFormat123"})
    assert response.status_code == 401


def test_protected_route_invalid_token(client):
    """Test accessing protected route with invalid JWT returns 401."""
    response = client.get("/bookings/", headers={"Authorization": "Bearer not.a.valid.jwt"})
    assert response.status_code == 401


def test_protected_route_valid_token(client, customer_headers):
    """Test accessing protected route with valid token returns 200."""
    response = client.get("/bookings/", headers=customer_headers)
    assert response.status_code == 200
