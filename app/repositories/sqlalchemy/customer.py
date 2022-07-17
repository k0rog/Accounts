from flask_sqlalchemy import SQLAlchemy
from injector import inject
from app.repositories.base import BaseCustomerRepository
from app.models.sqlalchemy.customer import Customer
from app.models.sqlalchemy.many_to_many import bank_accounts
from app.exceptions import AlreadyExistsException
from app.repositories.base import BaseBankAccountRepository


class CustomerRepository(BaseCustomerRepository):
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
            bank_account_repository: BaseBankAccountRepository
    ):
        self._storage = storage
        self._bank_account_repository = bank_account_repository

    def check_customer(self, passport_number: str) -> bool:
        return self._storage.session.query(
            Customer.passport_number
        ).filter_by(passport_number=passport_number).first() is not None

    def create_customer(self, data: dict) -> Customer:
        if self.check_customer(data['passport_number']):
            raise AlreadyExistsException('Customer already exists!')

        customer = Customer(
            passport_number=data['passport_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
        )

        bank_account = self._bank_account_repository.create_bank_account(**data['bank_account'])

        customer.bank_accounts.append(bank_account)

        self._storage.session.add(customer)
        self._storage.session.commit()

        return customer

    def get_customer_by_passport_number(self, passport_number: str) -> Customer:
        return self._storage.session.query(
            Customer
        ).filter_by(passport_number=passport_number).first()

    def has_bank_account(self, passport_number: str) -> bool:
        return self._storage.session.query(
            bank_accounts
        ).filter_by(customer_id=passport_number).first() is not None
