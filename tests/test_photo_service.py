import os
from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from app.services.photo_service import PhotoValidationError, save_photo


PNG_BYTES = b"\x89PNG\r\n\x1a\nvalid image bytes"


def make_file(content=PNG_BYTES, filename="evidence.png"):
    return FileStorage(stream=BytesIO(content), filename=filename)


def test_valid_image_gets_generated_safe_filename(app):
    filename = save_photo(make_file(filename="../../unsafe.png"), app.config["UPLOAD_FOLDER"])

    try:
        assert filename.endswith(".png")
        assert filename != "../../unsafe.png"
        assert os.path.basename(filename) == filename
        assert os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    finally:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))


def test_missing_image_is_allowed(app):
    assert save_photo(None, app.config["UPLOAD_FOLDER"]) is None


def test_unsupported_image_type_is_rejected(app):
    with pytest.raises(PhotoValidationError):
        save_photo(make_file(filename="evidence.txt"), app.config["UPLOAD_FOLDER"])


def test_oversized_image_is_rejected(app):
    with pytest.raises(PhotoValidationError, match="5 MB"):
        save_photo(
            make_file(content=b"x" * (5 * 1024 * 1024 + 1), filename="evidence.png"),
            app.config["UPLOAD_FOLDER"],
        )


def test_image_signature_must_match_extension(app):
    with pytest.raises(PhotoValidationError, match="valid image"):
        save_photo(make_file(content=b"not a png", filename="evidence.png"), app.config["UPLOAD_FOLDER"])
