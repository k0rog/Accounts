from app.exceptions import DoesNotExistException
from app.repositories.sqlalchemy.customer import CustomerRepository
from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.models.sqlalchemy.customer import Customer
from injector import inject


class CustomerService:
    @inject
    def __init__(
        self,
        customer_repository: CustomerRepository,
        bank_account_repository: BankAccountRepository
    ):
        self._customer_repository = customer_repository
        self._bank_account_repository = bank_account_repository

    def create(self, data: dict) -> Customer:
        """Creates customer and bank account for him.
        Customer can't exist without bank account due to domain constraints"""
        customer = self._customer_repository.create(data)

        self._bank_account_repository.create(data['bank_account'], customer.uuid)

        return customer

    def delete(self, uuid: str) -> None:
        is_deleted = self._customer_repository.delete(uuid)

        if not is_deleted:
            raise DoesNotExistException('Customer does not exist!')

    def update(self, uuid: str, data: dict) -> None:
        self._customer_repository.update(uuid, data)

    def get_by_uuid(self, uuid: str) -> Customer:
        return self._customer_repository.get_by_uuid(uuid)
