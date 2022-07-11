from app.storage.sqlalchemy import db
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model):
    passport_number = db.Column(db.String(9), primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String())
    _password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)
