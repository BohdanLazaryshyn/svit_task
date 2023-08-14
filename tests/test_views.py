from urllib.parse import urljoin

import pytest
from flask import url_for
from flask_login import current_user, login_user

from app import app
from config import db
from models import User, Log


@pytest.fixture
def app_test():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_db.sqlite"
    with app.app_context():
        db.create_all()
        yield db
        db.session.rollback()


@pytest.fixture
def client(app_test):
    with app.test_client() as client:
        yield client


@pytest.fixture
def user():
    existing_user = User.query.filter_by(username="testuser").first()
    if existing_user is None:
        user = User(
            username="testuser",
            email="test@example.com"
        )
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()
        return user
    return existing_user


@pytest.fixture
def authenticated_user(client, user):
    client.post("/login", data=dict(
        username=user.username,
        password="testpassword"
    ), follow_redirects=True)
    login_user(user)
    return user


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Please sign in" in response.data


def test_login(client, authenticated_user):
    assert current_user.is_authenticated


def test_login_invalid_credentials(client, user):
    response = client.post("/login", data=dict(
        username=user.username,
        password="wrongpassword"
    ), follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated


def test_logout(client, authenticated_user):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated


def test_index_page_not_authorized(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"You are not logged in!" in response.data


def test_index_page_authorized(client, authenticated_user):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Upload Files" in response.data


def test_upload_invalid_file_extension(client, authenticated_user):
    data = {"file": (open("images.jpg", "rb"), "images.jpg")}
    response = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid file extension" in response.data
    assert Log.query.count() == 0


def test_upload_valid_txt_file(client, authenticated_user):
    data = {"file": (open("test.txt", "rb"), "test.txt")}
    response = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert Log.query.count() == 1


def test_search_logs_not_authorized(client):
    response = client.get("/search")
    assert response.status_code == 302
    assert response.location == "/login"


def test_log_detail(client, authenticated_user):
    log = Log(content="Test log content", file_path="test.log")
    db.session.add(log)
    db.session.commit()

    response = client.get(f"/log/{log.id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Log Details" in response.data
    assert b"Test log content" in response.data


def test_unpack_archive_txt_file(client):
    data = {"file": (open("test.txt", "rb"), "test.txt")}
    response = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert Log.query.count() == 1

    with app.app_context():
        log = Log.query.first()
        assert log is not None
        assert "test content" in log.content


if __name__ == "__main__":
    pytest.main()
