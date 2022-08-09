from app.storage.sqlalchemy import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Customer(db.Model):
    uuid = db.Column(db.String(40), primary_key=True, default=generate_uuid)
    passport_number = db.Column(db.String(9), unique=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)
