from typing import Union

from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.models.sqlalchemy.bank_account import BankAccount
from app.exceptions import DoesNotExistException


class BankAccountService:
    def __init__(
        self,
        bank_account_repository: BankAccountRepository
    ):
        self._bank_account_repository = bank_account_repository

    def create(self, data: dict, customer_uuid: str) -> BankAccount:
        return self._bank_account_repository.create(data, customer_uuid)

    def update_balance_by_amount(self, iban: str, amount: Union[float, int]) -> None:
        self._bank_account_repository.update_balance_by_amount(iban, amount)

    def delete(self, iban: str) -> None:
        is_deleted = self._bank_account_repository.delete(iban)

        if not is_deleted:
            raise DoesNotExistException('BankAccount does not exist!')

    def add_bank_account_for_customer(self, iban: str, customer_uuid: str):
        self._bank_account_repository.assign_to_customer(iban, customer_uuid)

    def delete_owned_by_customer_bank_accounts(self, customer_uuid: str):
        bank_accounts = self._bank_account_repository.get_owned_by_customer(customer_uuid)

        self._bank_account_repository.bulk_delete([
            bank_account.IBAN for bank_account in bank_accounts
        ])

    def get_by_iban(self, iban: str) -> BankAccount:
        return self._bank_account_repository.get_by_iban(iban)
