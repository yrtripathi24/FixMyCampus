from app import create_app


def test_health_endpoint_is_available(app):
    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_production_configuration_enables_secure_cookie_settings(monkeypatch):
    monkeypatch.setenv("FIXMYCAMPUS_ENV", "production")
    monkeypatch.setenv("FIXMYCAMPUS_SECRET_KEY", "test-production-secret")
    configured_app = create_app({"TESTING": True, "DATABASE": ":memory:"})

    assert configured_app.config["SECRET_KEY"] == "test-production-secret"
    assert configured_app.config["SESSION_COOKIE_SECURE"] is True
    assert configured_app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert configured_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_wsgi_exports_application():
    from wsgi import app

    assert app.name == "app"
