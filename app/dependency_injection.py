from flask import Config, Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from injector import Binder, Module, singleton

from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.repositories.sqlalchemy.customer import CustomerRepository
from app.services.customer import CustomerService
from app.storage.sqlalchemy import configure_db


class SQLAlchemyModule(Module):
    def __init__(self, app: Flask, config: Config):
        self.app = app
        self.config = config

    def configure(self, binder: Binder):
        sqlalchemy_storage = configure_db(self.app)
        Migrate(self.app, sqlalchemy_storage, compare_type=True)

        binder.bind(interface=SQLAlchemy, to=sqlalchemy_storage, scope=singleton)
        binder.bind(interface=Config, to=self.config, scope=singleton)
        binder.bind(interface=BankAccountRepository, to=BankAccountRepository, scope=singleton)
        binder.bind(interface=CustomerRepository, to=CustomerRepository, scope=singleton)

        binder.bind(interface=CustomerService, to=CustomerService, scope=singleton)


