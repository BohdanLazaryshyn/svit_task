from flask_login import UserMixin
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash, check_password_hash

from config import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Log(db.Model):

    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=text("datetime(CURRENT_TIMESTAMP, 'localtime')"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<Log {self.id}>"
