from flask import Config
from flask_sqlalchemy import SQLAlchemy
from injector import inject
from app.repositories.base import BaseBankAccountRepository
from app.models.sqlalchemy.bank_account import BankAccount


class BankAccountRepository(BaseBankAccountRepository):
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
            config: Config
    ):
        self._storage = storage
        self._config = config

    def create_bank_account(self, currency: str, balance: float = 0.0):
        iban = self.get_unique_iban()

        bank_account = BankAccount(
            IBAN=iban,
            currency=currency,
            balance=balance,
        )

        self._storage.session.add(bank_account)
        self._storage.session.commit()

        return bank_account

    def get_unique_iban(self):
        return BankAccount.generate_iban(
            self._config['IBAN_COUNTRY_IDENTIFIER'],
            self._config['IBAN_BANK_IDENTIFIER'],
            int(self._config['IBAN_BBAN_LENGTH'])
        )
