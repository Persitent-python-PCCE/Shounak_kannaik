"""
File upload and validation tests.
"""

from common.file_utils import save_upload
from common.validators import validate_email


def test_file_upload_stub():
    """Test file upload utility stub."""
    result = save_upload(None, "static/uploads/posters")
    assert result is None


def test_email_validation():
    """Test email validation utility."""
    assert validate_email("user@example.com") is True
    assert validate_email("invalid-email") is False
    assert validate_email("") is False
