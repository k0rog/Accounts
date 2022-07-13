from flask_migrate import Migrate
from injector import Module, Binder, singleton
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.storage.sqlalchemy import configure_db
from app.repositories.base import BaseBankAccountRepository, BaseCustomerRepository
from app.repositories.sqlalchemy.customer import CustomerRepository
from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from flask import Config


class SQLAlchemyModule(Module):
    def __init__(self, app: Flask, config: Config):
        self.app = app
        self.config = config

    def configure(self, binder: Binder):
        sqlalchemy_storage = configure_db(self.app)
        Migrate(self.app, sqlalchemy_storage, compare_type=True)

        binder.bind(interface=SQLAlchemy, to=sqlalchemy_storage, scope=singleton)
        binder.bind(interface=Config, to=self.config, scope=singleton)
        binder.bind(interface=BaseBankAccountRepository, to=BankAccountRepository, scope=singleton)
        binder.bind(interface=BaseCustomerRepository, to=CustomerRepository, scope=singleton)
