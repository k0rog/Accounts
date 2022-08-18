from typing import Union

from flask import Config
from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from app.exceptions import DoesNotExistException, AlreadyExistException
from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.many_to_many import AssociationBankAccountCustomer


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
                self._storage.session.commit()

                break
            except IntegrityError:
                '''There's very small chance to generate duplicated IBAN
                But since this chance still exists, we have to repeat the operation'''
                self._storage.session.rollback()
            except DataError:
                self._storage.session.rollback()
                raise DoesNotExistException('Currency does not exist!')

        association_row = AssociationBankAccountCustomer(
            bank_account_id=bank_account.IBAN,
            customer_id=customer_uuid
        )

        self._storage.session.add(association_row)
        self._storage.session.commit()

        return bank_account

    def get_by_iban(self, iban: str) -> BankAccount:
        bank_account = self._storage.session.query(
            BankAccount
        ).filter_by(IBAN=iban).first()

        if not bank_account:
            raise DoesNotExistException('BankAccount does not exist!')

        return bank_account

    def get_owned_by_customer(self, customer_uuid) -> list[BankAccount]:
        return self._storage.session.query(
            BankAccount
        ).join(
            AssociationBankAccountCustomer
        ).filter(
            AssociationBankAccountCustomer.customer_id == customer_uuid
        ).all()

    def delete(self, iban: str) -> bool:
        is_deleted = self._storage.session.query(
            BankAccount
        ).filter_by(IBAN=iban).delete()

        self._storage.session.commit()

        return is_deleted

    def bulk_delete(self, ibans: list[str]) -> None:
        is_deleted = self._storage.session.query(
            BankAccount
        ).filter(BankAccount.IBAN.in_(ibans)).delete()

        self._storage.session.commit()

        return is_deleted

    def assign_to_customer(self, iban: str, customer_uuid: str) -> None:
        try:
            association_row = AssociationBankAccountCustomer(
                bank_account_id=iban,
                customer_id=customer_uuid
            )

            self._storage.session.add(association_row)
            self._storage.session.flush()

        except IntegrityError as e:
            self._storage.session.rollback()

            if isinstance(e.orig, ForeignKeyViolation):
                raise DoesNotExistException('BankAccount does not exist!')

            if isinstance(e.orig, UniqueViolation):
                raise AlreadyExistException('Relation already exist!')

            raise e

        self._storage.session.commit()

    def update_balance_by_amount(self, iban: str, amount: Union[int, float]) -> bool:
        result = self._storage.session.query(
            BankAccount
        ).filter_by(IBAN=iban).update({
            BankAccount.balance: BankAccount.balance + amount
        })

        self._storage.session.commit()

        return result
