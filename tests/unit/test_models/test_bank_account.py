import re
from app.models.sqlalchemy.bank_account import BankAccount


def test_iban_generation():
    iban = BankAccount.generate_iban(
        'BY',
        'JPCB',
        20
    )

    assert re.match(r'^[a-zA-Z]{2}[\da-zA-Z]{6}\d{20}$', iban) is not None
