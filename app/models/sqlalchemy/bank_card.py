from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

from app.storage.sqlalchemy import db
from app.utils.luhn_algorithm import calculate_luhn
from app.utils.random_sequence_generator import generate_random_digit_sequence
from app.exceptions import AccessDeniedException


def generate_card_number():
    config = current_app.config

    payment_system_code = config['CARD_NUMBER_PAYMENT_SYSTEM_CODE']
    bank_card_bank_identifier = config['CARD_NUMBER_BANK_IDENTIFIER']
    customer_identifier_length = int(config['CARD_NUMBER_CUSTOMER_IDENTIFIED_LENGTH'])

    customer_identifier = generate_random_digit_sequence(customer_identifier_length)

    code = str(payment_system_code) + str(bank_card_bank_identifier) + customer_identifier
    check_digit = calculate_luhn(code)

    return code + str(check_digit)


class BankCard(db.Model):
    __tablename__ = 'bank_card'

    def __eq__(self, other):
        return self.card_number == other

    card_number = db.Column(db.String(16), primary_key=True, default=generate_card_number)
    expiration_date = db.Column(db.Date(), nullable=False)

    _pin_hash = db.Column(db.String(256))
    _cvv_hash = db.Column(db.String(256))

    bank_account_iban = db.Column(db.String, db.ForeignKey('bank_account.IBAN', ondelete='CASCADE'))
    bank_account = db.relationship('BankAccount',
                                   backref=db.backref('cards', lazy=True))

    def set_pin(self, pin):
        if self._pin_hash:
            raise AccessDeniedException('You cannot modify _pin_hash field!')

        self._pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self._pin_hash, pin)

    def set_cvv(self, cvv):
        if self._cvv_hash:
            raise AccessDeniedException('You cannot modify _cvv_hash field!')

        self._cvv_hash = generate_password_hash(cvv)

    def check_cvv(self, cvv):
        return check_password_hash(self._cvv_hash, cvv)

    @staticmethod
    def generate_pin():
        return generate_random_digit_sequence(4)

    @staticmethod
    def generate_cvv():
        return generate_random_digit_sequence(3)
