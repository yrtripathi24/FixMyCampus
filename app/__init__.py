import os

import click
from flask import Flask
from flask.cli import with_appcontext

from app.database import close_db, init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "fixmycampus.sqlite"),
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    return app


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the configured SQLite database."""
    init_db()
