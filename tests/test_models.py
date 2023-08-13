import pytest
from app import app, db
from models import User, Log


@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_db.sqlite"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_create_user(test_client):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="testpassword"
    )
    db.session.add(user)
    db.session.commit()
    assert User.query.filter_by(username="testuser").first() is not None


def test_create_log(test_client):
    log = Log(content="Test log content", file_path="/test/path")
    db.session.add(log)
    db.session.commit()
    assert Log.query.filter_by(content="Test log content").first() is not None
