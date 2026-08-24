
import io
import pytest
from werkzeug.datastructures import FileStorage
from common.file_utils import allowed_file, validate_file, save_uploaded_file, MAX_FILE_SIZE_BYTES
from common.validators import validate_email


def test_allowed_file():
    assert allowed_file("document.pdf") is True
    assert allowed_file("poster.jpg") is True
    assert allowed_file("poster.png") is True
    assert allowed_file("poster.webp") is True
    assert allowed_file("script.py") is False
    assert allowed_file("malicious.exe") is False
    assert allowed_file("no_extension") is False
    assert allowed_file("") is False


def test_validate_file_valid():
    stream = io.BytesIO(b"valid content")
    file_storage = FileStorage(stream=stream, filename="test.png", content_type="image/png")
    assert validate_file(file_storage) is True


def test_validate_file_disallowed_extension():
    stream = io.BytesIO(b"malicious script")
    file_storage = FileStorage(stream=stream, filename="script.sh", content_type="text/plain")
    with pytest.raises(ValueError, match="File extension is not allowed"):
        validate_file(file_storage)


def test_validate_file_empty_file():
    stream = io.BytesIO(b"")
    file_storage = FileStorage(stream=stream, filename="empty.pdf")
    with pytest.raises(ValueError, match="Uploaded file is empty"):
        validate_file(file_storage)


def test_validate_file_exceeding_max_size():

    oversized_data = b"0" * (MAX_FILE_SIZE_BYTES + 1024)
    stream = io.BytesIO(oversized_data)
    file_storage = FileStorage(stream=stream, filename="large.pdf")
    with pytest.raises(ValueError, match="File size exceeds maximum allowed limit"):
        validate_file(file_storage)


def test_save_uploaded_file(tmp_path):
    stream = io.BytesIO(b"dummy image data")
    file_storage = FileStorage(stream=stream, filename="test_poster.jpg")
    target_dir = str(tmp_path / "posters")

    saved_path = save_uploaded_file(file_storage, target_dir, prefix="event")
    assert saved_path is not None
    assert "test_poster.jpg" in saved_path
    assert "event_" in saved_path


def test_admin_create_event_with_poster(client, admin_headers):
    poster_data = io.BytesIO(b"fake poster bytes")
    payload = {
        "name": "Rock Fest 2026",
        "about": "Annual rock music festival",
        "age_rating": "U/A 16+",
        "poster_image": (poster_data, "rock_fest.png")
    }
    response = client.post("/admin/events", data=payload, headers=admin_headers, content_type="multipart/form-data")
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Event created successfully"
    assert data["event"]["name"] == "Rock Fest 2026"
    assert data["event"]["poster_image_path"] is not None
    assert "rock_fest.png" in data["event"]["poster_image_path"]


def test_user_upload_document_endpoint(client, customer_headers):
    doc_data = io.BytesIO(b"%PDF-1.4 voter card")
    payload = {
        "doc_type": "Voter ID",
        "id_document": (doc_data, "voter_card.pdf")
    }
    response = client.post("/documents/upload", data=payload, headers=customer_headers, content_type="multipart/form-data")
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Document uploaded successfully"
    assert data["document"]["doc_type"] == "Voter ID"
    assert "voter_card.pdf" in data["document"]["file_path"]
