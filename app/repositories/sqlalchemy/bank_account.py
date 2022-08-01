from flask import Config
from flask_sqlalchemy import SQLAlchemy
from injector import inject
from app.models.sqlalchemy.bank_account import BankAccount
from sqlalchemy.exc import IntegrityError


class BankAccountRepository:
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
            config: Config
    ):
        self._storage = storage
        self._config = config

    def create_bank_account(self, currency: str, balance: float = 0.0):
        while True:
            try:
                iban = self._get_unique_iban()

                bank_account = BankAccount(
                    IBAN=iban,
                    currency=currency,
                    balance=balance,
                )

                self._storage.session.add(bank_account)
                self._storage.session.commit()

                break
            except IntegrityError:
                '''There's very small chance to generate duplicated IBAN
                But since this chance still exists, we have to repeat the operation'''

        return bank_account

    def _get_unique_iban(self):
        return BankAccount.generate_iban(
            self._config['IBAN_COUNTRY_IDENTIFIER'],
            self._config['IBAN_BANK_IDENTIFIER'],
            int(self._config['IBAN_BBAN_LENGTH'])
        )
