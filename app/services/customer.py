from app.repositories.sqlalchemy.customer import CustomerRepository
from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.models.sqlalchemy.customer import Customer


class CustomerService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        bank_account_repository: BankAccountRepository
    ):
        self._customer_repository = customer_repository
        self._bank_account_repository = bank_account_repository

    def create(self, data: dict) -> Customer:
        raise NotImplementedError

    def delete(self, uuid: str) -> None:
        raise NotImplementedError

    def update(self, uuid: str, data: dict) -> None:
        raise NotImplementedError

    def get_by_uuid(self, uuid: str) -> Customer:
        raise NotImplementedError
