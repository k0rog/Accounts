from flask_sqlalchemy import SQLAlchemy
from injector import inject
from app.models.sqlalchemy.customer import Customer
from app.models.sqlalchemy.many_to_many import bank_accounts
from app.exceptions import AlreadyExistException, DoesNotExistException
from sqlalchemy.exc import IntegrityError


class CustomerRepository:
    @inject
    def __init__(
        self,
        storage: SQLAlchemy,
    ):
        self._storage = storage

    def is_exists(self, uuid: str) -> bool:
        return self._storage.session.query(
            Customer.uuid
        ).filter_by(uuid=uuid).first() is not None

    def create(self, data: dict) -> Customer:
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
            self._storage.session.rollback()
            raise AlreadyExistException('Customer already exist!')

        return customer

    def update(self, uuid: str, data: dict):
        try:
            self._storage.session.query(
                Customer
            ).filter_by(uuid=uuid).update(data)

            self._storage.session.commit()
        except IntegrityError:
            self._storage.session.rollback()
            raise AlreadyExistException('Customer already exist!')

    def delete(self, uuid: str):
        """Deletes customer
        We're forced to perform check query to inform the user if the deletion had no effect"""

        if not self.is_exists(uuid):
            raise DoesNotExistException('Customer does not exist!')

        self._storage.session.query(
            Customer
        ).filter_by(uuid=uuid).delete()

        self._storage.session.commit()

    def get_by_uuid(self, uuid: str) -> Customer:
        customer = self._storage.session.query(
            Customer
        ).filter_by(uuid=uuid).first()

        if not customer:
            raise DoesNotExistException('Customer does not exist!')

        return customer

    def has_bank_account(self, uuid: str) -> bool:
        return self._storage.session.query(
            bank_accounts.customer_id
        ).filter_by(customer_id=uuid).first() is not None
