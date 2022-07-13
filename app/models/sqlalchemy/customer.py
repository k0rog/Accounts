from app.storage.sqlalchemy import db
from app.models.sqlalchemy.many_to_many import bank_accounts
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model):
    passport_number = db.Column(db.String(9), primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String(256))
    bank_accounts = db.relationship('BankAccount', secondary=bank_accounts, lazy='subquery',
                                    backref=db.backref('customers', lazy=True))

    def set_password(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)
