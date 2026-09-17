import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app(tmp_path):
    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-key"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path / 'test.sqlite'}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        UPLOAD_FOLDER = tmp_path / "uploads"
        REPORT_FOLDER = tmp_path / "reports"
        MODEL_DIR = tmp_path / "models"
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    application = create_app(TestConfig)
    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def perform(username, password):
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
        )

    return perform
