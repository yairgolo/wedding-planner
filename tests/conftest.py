import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User, Wedding


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        db.session.add(
            User(
                email="admin@example.com",
                display_name="יאיר",
                password_hash=generate_password_hash("password123"),
                is_admin=True,
            )
        )
        db.session.add(Wedding(partner_one="יאיר", partner_two="רבקה"))
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
