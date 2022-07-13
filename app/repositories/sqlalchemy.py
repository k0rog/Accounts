from flask import Config
from flask_sqlalchemy import SQLAlchemy
from injector import inject
from app.repositories.base import BaseRepository
from app.models.sqlalchemy import Customer, BankAccount
from app.exceptions import AlreadyExistsException


class SQLAlchemyRepository(BaseRepository):
    @inject
    def __init__(self, storage: SQLAlchemy, config: Config):
        self.storage = storage
        self.config = config

    def check_customer(self, passport_number: str) -> bool:
        return self.storage.session.query(Customer.passport_number). \
                   filter_by(passport_number=passport_number).first() is not None

    def create_customer(self, data: dict) -> Customer:
        if self.check_customer(data['passport_number']):
            raise AlreadyExistsException('Customer already exists!')

        customer = Customer(
            passport_number=data['passport_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
        )

        bank_account = self.create_bank_account(**data['bank_account'])

        customer.bank_accounts.append(bank_account)

        self.storage.session.add(customer)
        self.storage.session.commit()

        return customer

    def create_bank_account(self, currency: str, balance: float = 0.0):
        iban = self.get_unique_iban()

        bank_account = BankAccount(
            IBAN=iban,
            currency=currency,
            balance=balance,
        )

        return bank_account

    def get_unique_iban(self):
        while True:
            iban = BankAccount.generate_iban(self.config['IBAN_COUNTRY_IDENTIFIER'],
                                             self.config['IBAN_BANK_IDENTIFIER'],
                                             int(self.config['IBAN_BBAN_LENGTH']))

            if not self.check_bank_account(iban):
                break
        return iban

    def check_bank_account(self, iban: str) -> bool:
        return self.storage.session.query(BankAccount.IBAN). \
                   filter_by(IBAN=iban).first() is not None
