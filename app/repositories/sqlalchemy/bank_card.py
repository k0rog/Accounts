from flask_sqlalchemy import SQLAlchemy
from injector import inject

from app.models.sqlalchemy.bank_card import BankCard


class BankCardRepository:
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
    ):
        self._storage = storage

    def create(self, data: dict, bank_account_iban: str) -> tuple[BankCard, str, str]:
        raise NotImplementedError

    def get_by_card_number(self, card_number: str) -> BankCard:
        raise NotImplementedError

    def get_attached_to_bank_account(self, customer_uuid) -> list[BankCard]:
        raise NotImplementedError

    def delete(self, card_number: str) -> None:
        raise NotImplementedError

    def batch_delete(self, card_numbers: list[str]) -> None:
        raise NotImplementedError
