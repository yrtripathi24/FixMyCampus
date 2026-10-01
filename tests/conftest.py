import pytest

from app import create_app
from app.database import init_db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": ":memory:",
        }
    )
    with app.app_context():
        init_db()
        yield app
