import os

import click
from flask import Flask, render_template_string
from flask.cli import with_appcontext
from werkzeug.exceptions import RequestEntityTooLarge

from app.database import close_db, init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    environment = os.environ.get("FIXMYCAMPUS_ENV", "development")
    secret_key = os.environ.get("FIXMYCAMPUS_SECRET_KEY")
    if environment == "production" and not secret_key:
        raise RuntimeError("FIXMYCAMPUS_SECRET_KEY is required in production.")
    app.config.from_mapping(
        SECRET_KEY=secret_key or "dev",
        ENVIRONMENT=environment,
        DEBUG=os.environ.get("FIXMYCAMPUS_DEBUG", "0") == "1",
        DATABASE=os.path.join(app.instance_path, "fixmycampus.sqlite"),
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(_error):
        return render_template_string(
            "<h1>Upload too large</h1><p>Images must be 5 MB or smaller.</p>"
        ), 413

    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    return app


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the configured SQLite database."""
    init_db()
