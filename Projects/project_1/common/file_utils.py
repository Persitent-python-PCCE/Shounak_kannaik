import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024 

def allowed_file(filename: str, allowed_extensions: set = None) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    allowed = allowed_extensions if allowed_extensions is not None else ALLOWED_EXTENSIONS
    return ext in allowed


def validate_file(file_storage, allowed_extensions: set = None, max_size_bytes: int = MAX_FILE_SIZE_BYTES, required: bool = True) -> bool:
    if file_storage is None or not getattr(file_storage, "filename", None) or file_storage.filename.strip() == "":
        if required:
            raise ValueError("No file uploaded or file is empty.")
        return False


    allowed = allowed_extensions if allowed_extensions is not None else ALLOWED_EXTENSIONS
    if not allowed_file(file_storage.filename, allowed):
        allowed_str = ", ".join(sorted(allowed))
        raise ValueError(f"File extension is not allowed. Allowed extensions: {allowed_str}")


    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)                                              

    if size == 0:
        raise ValueError("Uploaded file is empty.")

    if size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise ValueError(f"File size exceeds maximum allowed limit of {max_mb:.1f}MB.")

    return True


def save_uploaded_file(file_storage, target_folder: str, prefix: str = None) -> str:
    if file_storage is None or not getattr(file_storage, "filename", None):
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        ext = "bin"
        if "." in file_storage.filename:
            ext = file_storage.filename.rsplit(".", 1)[1].lower()
        filename = f"upload.{ext}"

    unique_id = uuid.uuid4().hex[:12]
    if prefix:
        saved_filename = f"{prefix}_{unique_id}_{filename}"
    else:
        saved_filename = f"{unique_id}_{filename}"


    os.makedirs(target_folder, exist_ok=True)

    destination_path = os.path.join(target_folder, saved_filename)
    file_storage.seek(0)
    file_storage.save(destination_path)


    return destination_path.replace("\\", "/")


def save_upload(file_storage, target_folder: str):
    return save_uploaded_file(file_storage, target_folder)
