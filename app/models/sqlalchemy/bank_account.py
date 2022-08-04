import enum
import random
import hashlib
from flask import current_app

from app.storage.sqlalchemy import db


class CurrencyEnum(enum.Enum):
    BYN = 'BYN'
    USD = 'USD'
    EUR = 'EUR'


def generate_iban():
    config = current_app.config
    country_code = config['IBAN_COUNTRY_IDENTIFIER']
    bank_identifier = config['IBAN_BANK_IDENTIFIER']
    iban_length = int(config['IBAN_BBAN_LENGTH'])

    bban = ''.join(["%s" % random.randint(0, 9) for _ in range(0, iban_length)])
    bban_hash = hashlib.shake_256(bban.encode('utf-8')).hexdigest(length=1)

    iban = country_code + bban_hash + bank_identifier + bban

    return iban.upper()


class BankAccount(db.Model):
    __tablename__ = 'bank_account'

    IBAN = db.Column(db.String(34), primary_key=True, default=generate_iban)
    currency = db.Column(db.Enum(CurrencyEnum), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
