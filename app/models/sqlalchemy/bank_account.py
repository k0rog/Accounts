import enum
import random
import hashlib
from app.storage.sqlalchemy import db


class CurrencyEnum(enum.Enum):
    BYN = 'BYN'
    USD = 'USD'
    EUR = 'EUR'


class BankAccount(db.Model):
    __tablename__ = 'bank_account'

    IBAN = db.Column(db.String(34), primary_key=True)
    currency = db.Column(db.Enum(CurrencyEnum), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)

    @staticmethod
    def generate_iban(country_code: str, bank_identifier: str, iban_length: int):
        bban = ''.join(["%s" % random.randint(0, 9) for _ in range(0, iban_length)])
        bban_hash = hashlib.shake_256(bban.encode('utf-8')).hexdigest(length=1)

        iban = country_code + bban_hash + bank_identifier + bban

        return iban.upper()
