from flask_sqlalchemy import SQLAlchemy
from injector import inject


class BankCardRepository:
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
    ):
        self._storage = storage
