from typing import Union

from flask import Config
from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy.exc import IntegrityError

from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.many_to_many import bank_accounts


class BankAccountRepository:
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
            config: Config
    ):
        self._storage = storage
        self._config = config

    def create(self, data: dict, customer_uuid: str):
        while True:
            try:
                bank_account = BankAccount(
                    currency=data['currency'],
                    balance=data['balance'] if 'balance' in data else 0.0,
                )

                self._storage.session.add(bank_account)
                self._storage.session.flush()

                break
            except IntegrityError:
                '''There's very small chance to generate duplicated IBAN
                But since this chance still exists, we have to repeat the operation'''
                self._storage.session.rollback()

        insert_statement = bank_accounts.insert().values(
            customer_id=customer_uuid,
            bank_account_id=bank_account.IBAN
        )

        self._storage.session.execute(insert_statement)
        self._storage.session.commit()

        return bank_account

    def get_by_iban(self, iban: str) -> BankAccount:
        raise NotImplementedError

    def get_owned_by_customer(self, customer_uuid) -> list[BankAccount]:
        raise NotImplementedError

    def delete(self, iban: str) -> None:
        raise NotImplementedError

    def batch_delete(self, ibans: list[str]) -> None:
        raise NotImplementedError

    def assign_to_customer(self, iban: str, customer_uuid: str) -> None:
        raise NotImplementedError

    def update_balance_by_amount(self, iban: str, amount: Union[int, float]) -> None:
        raise NotImplementedError
