import pytest
from flask_login import current_user

from app import app, db, Log
from models import User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_db.sqlite"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def user():
    user = User(
        username="testuser",
        email="test@example.com"
    )
    user.set_password("testpassword")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_user(client, user):
    client.post("/login", data=dict(
        username=user.username,
        password="testpassword"
    ), follow_redirects=True)
    return user


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Please sign in" in response.data


def test_login(client, user):
    response = client.post("/login", data=dict(
        username=user.username,
        password="testpassword"
    ))
    assert response.status_code == 200
    assert current_user.username == user.username


def test_login_invalid_credentials(client, user):
    response = client.post("/login", data=dict(
        username=user.username,
        password="wrongpassword"
    ), follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated


def test_login_already_authenticated(client, authenticated_user):
    response = client.get("/login", follow_redirects=True)
    assert response.status_code == 200
    assert b"You are already logged in." in response.data


def test_register(client):
    response = client.post("/register", data=dict(
        username="newuser",
        email="newuser@example.com",
        password="newpassword"
    ), follow_redirects=True)
    assert response.status_code == 200
    assert current_user.username == "newuser"


def test_register_existing_username(client, user):
    response = client.post("/register", data=dict(
        username=user.username,
        email="newemail@example.com",
        password="newpassword"
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"Username already taken." in response.data
    assert not current_user.is_authenticated


def test_register_already_authenticated(client, authenticated_user):
    response = client.get("/register", follow_redirects=True)
    assert response.status_code == 200
    assert b"You are already registered." in response.data


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


def test_upload_valid_txt_file(client):
    data = {"file": (open("test.txt", "rb"), "test.txt")}
    response = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert Log.query.count() == 1


def test_upload_invalid_file_extension(client):
    data = {"file": (open("images.jpg", "rb"), "images.jpg")}
    response = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid file extension" in response.data
    assert Log.query.count() == 0


def test_search_logs(client):
    response = client.get("/search")
    assert response.status_code == 200
    assert b"Welcome!" in response.data
    assert b"You are not logged in!" in response.data


def test_log_detail(client):
    log = Log(content="Test log content")
    db.session.add(log)
    db.session.commit()

    response = client.get(f"/log/{log.id}")
    assert response.status_code == 200
    assert b"Test log content" in response.data


def test_invalid_log_detail(client):
    response = client.get("/log/999")
    assert response.status_code == 404


def test_unpack_archive_txt_file(client):
    data = {"file": (open("test.txt", "rb"), "test.txt")}
    response = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"File: test.txt uploaded successfully" in response.data

    with app.app_context():
        log = Log.query.first()
        assert log is not None
        assert log.content == "This is a test file.\n"


if __name__ == "__main__":
    pytest.main()
