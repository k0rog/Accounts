from app.storage.sqlalchemy import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum

bank_accounts = db.Table(
    'bank_accounts',
    db.Column('customer_id', db.String(9), db.ForeignKey('customer.passport_number'), primary_key=True),
    db.Column('bank_account_id', db.String(18), db.ForeignKey('bank_account.IBAN'), primary_key=True)
)


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


class CurrencyEnum(enum.Enum):
    BYN = 'BYN'
    USD = 'USD'
    EUR = 'EUR'


class BankAccount(db.Model):
    __tablename__ = 'bank_account'
    IBAN = db.Column(db.String(18), primary_key=True)
    currency = db.Column(db.Enum(CurrencyEnum), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)


class BankCard(db.Model):
    __tablename__ = 'bank_card'
    card_number = db.Column(db.String(16), primary_key=True)
    expiration_date = db.Column(db.Date(), nullable=False)
    CVV = db.Column(db.Integer, nullable=False)
    _pin_hash = db.Column(db.String(256))
    bank_account = db.relationship('BankAccount',
                                   backref=db.backref('cards', lazy=True))

    def set_pin(self, pin):
        self._pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self._pin_hash, pin)
