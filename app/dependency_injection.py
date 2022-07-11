from flask_migrate import Migrate
from injector import Module, Binder, singleton
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.storage.sqlalchemy import configure_db
from app.repositories.base import BaseRepository
from app.repositories.sqlalchemy import SQLAlchemyRepository


class SQLAlchemyModule(Module):
    def __init__(self, app: Flask):
        self.app = app

    def configure(self, binder: Binder):
        sqlalchemy_storage = configure_db(self.app)
        Migrate(self.app, sqlalchemy_storage)

        binder.bind(interface=SQLAlchemy, to=sqlalchemy_storage, scope=singleton)
        binder.bind(interface=BaseRepository, to=SQLAlchemyRepository, scope=singleton)
