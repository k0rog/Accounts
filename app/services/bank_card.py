from app.exceptions import DoesNotExistException
from app.repositories.sqlalchemy.bank_card import BankCardRepository
from app.models.sqlalchemy.bank_card import BankCard


class BankCardService:
    def __init__(
        self,
        bank_card_repository: BankCardRepository
    ):
        self._bank_card_repository = bank_card_repository

    def create(self, data: dict, bank_account_iban: str) -> tuple[BankCard, str, str]:
        return self._bank_card_repository.create(data, bank_account_iban)

    def delete(self, card_number: str) -> None:
        is_deleted = self._bank_card_repository.delete(card_number)

        if not is_deleted:
            raise DoesNotExistException('BankCard does not exist!')

    def delete_bank_cards_attached_to_bank_account(self, bank_account_iban: str) -> None:
        bank_cards = self._bank_card_repository.get_attached_to_bank_account(bank_account_iban)

        self._bank_card_repository.bulk_delete(
            [bank_card.card_number for bank_card in bank_cards]
        )

    def get_by_card_number(self, card_number: str) -> BankCard:
        return self._bank_card_repository.get_by_card_number(card_number)
