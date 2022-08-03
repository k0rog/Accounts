from app.repositories.sqlalchemy.bank_card import BankCardRepository
from app.models.sqlalchemy.bank_card import BankCard


class BankCardService:
    def __init__(
        self,
        bank_card_repository: BankCardRepository
    ):
        self._bank_card_repository = bank_card_repository

    def create(self, data: dict, bank_account_iban: str) -> tuple[BankCard, str, str]:
        raise NotImplementedError

    def delete(self, card_number: str) -> None:
        raise NotImplementedError

    def delete_bank_cards_attached_to_bank_account(self, bank_account_iban: str) -> None:
        raise NotImplementedError

    def get_by_card_number(self, card_number: str) -> BankCard:
        raise NotImplementedError
