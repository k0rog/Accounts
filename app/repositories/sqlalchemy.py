from flask_sqlalchemy import SQLAlchemy
from injector import inject
from app.repositories.base import BaseRepository
from app.models.sqlalchemy import Customer
from app.exceptions import AlreadyExists


class SQLAlchemyRepository(BaseRepository):
    @inject
    def __init__(self, storage: SQLAlchemy):
        self.storage = storage

    def check_customer(self, passport_number: str) -> bool:
        return self.storage.session.query(Customer.passport_number).\
                   filter_by(passport_number=passport_number).first() is not None

    def create_customer(self, data: dict) -> Customer:
        if self.check_customer(data['passport_number']):
            raise AlreadyExists('Customer already exists!')

        customer = Customer(
            passport_number=data['passport_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
        )

        self.storage.session.add(customer)
        self.storage.session.commit()

        return customer
