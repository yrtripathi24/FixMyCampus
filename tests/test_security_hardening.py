from io import BytesIO

from app import create_app
from app.repositories.incidents import create_incident
from app.repositories.reports import attach_report_to_incident, create_report


def test_security_headers_are_present(app):
    response = app.test_client().get("/")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "same-origin"


def test_user_text_is_escaped_in_confirmation(app):
    response = app.test_client().post(
        "/report",
        data={
            "category": "Other",
            "location": "Campus",
            "description": "<script>alert('x')</script>",
        },
    )

    assert response.status_code == 200
    assert b"<script>alert('x')</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_repeated_report_attachment_is_rejected(app):
    incident = create_incident("Broken light", "Electrical", "Block C")
    report = create_report("Broken light", "Electrical", "Block C")

    assert attach_report_to_incident(report.id, incident.id)
    assert not attach_report_to_incident(report.id, incident.id)


def test_upload_path_cannot_escape_upload_directory(app):
    response = app.test_client().get("/uploads/subfolder/secret.png")

    assert response.status_code == 404


def test_oversized_request_returns_clear_error(app):
    response = app.test_client().post(
        "/report",
        data={
            "category": "Other",
            "location": "Campus",
            "description": "Large upload",
            "photo": (BytesIO(b"x" * (5 * 1024 * 1024)), "large.png"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert b"Upload too large" in response.data


def test_development_defaults_do_not_enable_debug(app, monkeypatch):
    monkeypatch.delenv("FIXMYCAMPUS_DEBUG", raising=False)
    configured_app = create_app({"TESTING": True, "DATABASE": ":memory:"})

    assert configured_app.debug is False


def test_production_requires_explicit_secret(monkeypatch):
    monkeypatch.setenv("FIXMYCAMPUS_ENV", "production")
    monkeypatch.delenv("FIXMYCAMPUS_SECRET_KEY", raising=False)

    try:
        create_app({"TESTING": True, "DATABASE": ":memory:"})
    except RuntimeError as error:
        assert "SECRET_KEY" in str(error)
    else:
        raise AssertionError("Production app started without a secret key")
