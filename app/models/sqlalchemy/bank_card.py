from app.storage.sqlalchemy import db
from werkzeug.security import generate_password_hash, check_password_hash


class BankCard(db.Model):
    __tablename__ = 'bank_card'
    card_number = db.Column(db.String(16), primary_key=True)
    expiration_date = db.Column(db.Date(), nullable=False)
    CVV = db.Column(db.Integer, nullable=False)
    _pin_hash = db.Column(db.String(256))
    bank_account_iban = db.Column(db.String, db.ForeignKey('bank_account.IBAN'))
    bank_account = db.relationship('BankAccount',
                                   backref=db.backref('cards', lazy=True))

    def set_pin(self, pin):
        self._pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self._pin_hash, pin)
