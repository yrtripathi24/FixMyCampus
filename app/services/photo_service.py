import os
from pathlib import Path
from uuid import uuid4


MAX_PHOTO_SIZE = 5 * 1024 * 1024
ALLOWED_PHOTO_TYPES = {
    ".gif": ("image/gif", lambda data: data.startswith((b"GIF87a", b"GIF89a"))),
    ".jpeg": ("image/jpeg", lambda data: data.startswith(b"\xff\xd8\xff")),
    ".jpg": ("image/jpeg", lambda data: data.startswith(b"\xff\xd8\xff")),
    ".png": ("image/png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    ".webp": (
        "image/webp",
        lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP",
    ),
}


class PhotoValidationError(ValueError):
    pass


def save_photo(file_storage, upload_folder):
    if file_storage is None or not file_storage.filename:
        return None

    extension = Path(file_storage.filename).suffix.casefold()
    photo_type = ALLOWED_PHOTO_TYPES.get(extension)
    if photo_type is None:
        raise PhotoValidationError("Upload a PNG, JPEG, GIF, or WebP image.")

    content = file_storage.read(MAX_PHOTO_SIZE + 1)
    file_storage.seek(0)
    if len(content) > MAX_PHOTO_SIZE:
        raise PhotoValidationError("Image must be 5 MB or smaller.")
    if not photo_type[1](content):
        raise PhotoValidationError("The uploaded file is not a valid image.")

    filename = f"{uuid4().hex}{extension}"
    os.makedirs(upload_folder, exist_ok=True)
    with open(os.path.join(upload_folder, filename), "wb") as saved_file:
        saved_file.write(content)
    return filename
