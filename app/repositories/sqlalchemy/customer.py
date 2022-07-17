from flask_sqlalchemy import SQLAlchemy
from injector import inject
from app.repositories.base import BaseCustomerRepository
from app.models.sqlalchemy.customer import Customer
from app.models.sqlalchemy.many_to_many import bank_accounts
from app.exceptions import AlreadyExistsException
from app.repositories.base import BaseBankAccountRepository
from sqlalchemy.exc import IntegrityError


class CustomerRepository(BaseCustomerRepository):
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
            bank_account_repository: BaseBankAccountRepository
    ):
        self._storage = storage
        self._bank_account_repository = bank_account_repository

    def check_customer(self, uuid: str) -> bool:
        return self._storage.session.query(
            Customer.uuid
        ).filter_by(uuid=uuid).first() is not None

    def create_customer(self, data: dict) -> Customer:
        customer = Customer(
            passport_number=data['passport_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
        )

        try:
            self._storage.session.add(customer)
            self._storage.session.commit()
        except IntegrityError:
            raise AlreadyExistsException('Customer already exists!')

        bank_account = self._bank_account_repository.create_bank_account(**data['bank_account'])

        customer.bank_accounts.append(bank_account)

        self._storage.session.commit()

        return customer

    def update_customer(self, uuid: str, data: dict):
        self._storage.session.query(
            Customer
        ).filter_by(uuid=uuid).update(data)
        self._storage.session.commit()

    def get_customer(self, uuid: str) -> Customer:
        return self._storage.session.query(
            Customer
        ).filter_by(uuid=uuid).first()

    def has_bank_account(self, uuid: str) -> bool:
        return self._storage.session.query(
            bank_accounts
        ).filter_by(customer_id=uuid).first() is not None
