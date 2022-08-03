from typing import Union

from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.models.sqlalchemy.bank_account import BankAccount


class BankAccountService:
    def __init__(
        self,
        bank_account_repository: BankAccountRepository
    ):
        self._bank_account_repository = bank_account_repository

    def create(self, data: dict, customer_uuid: str) -> BankAccount:
        raise NotImplementedError

    def update_balance_by_amount(self, iban: str, amount: Union[float, int]) -> None:
        raise NotImplementedError

    def delete(self, iban: str) -> None:
        raise NotImplementedError

    def add_bank_account_for_customer(self, customer_uuid, iban):
        raise NotImplementedError

    def delete_owned_by_customer_bank_accounts(self, customer_uuid: str):
        raise NotImplementedError

    def get_by_iban(self, iban: str) -> BankAccount:
        raise NotImplementedError
