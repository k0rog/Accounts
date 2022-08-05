import hashlib

import pytest

from app.exceptions import DoesNotExistException
from app.models.sqlalchemy.bank_card import BankCard


BANK_CARD_DATA = {
    'expiration_date': '2025-05-05',
}

MockIBAN = 'MockIBAN'


class TestCreate:
    def test_has_card_number(self, bank_card_repository):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        assert hasattr(bank_card, 'card_number')

    def test_create(self, bank_card_repository):
        bank_card, pin, cvv = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        storage_bank_card = BankCard.query.filter_by(card_number=bank_card.card_number).first()

        assert storage_bank_card is not None

        assert storage_bank_card.expiration_date == BANK_CARD_DATA['expiration_date']
        assert storage_bank_card._cvv_hash == hashlib.sha256(cvv.encode('utf-8')).hexdigest()
        assert storage_bank_card._pin_hash == hashlib.sha256(pin.encode('utf-8')).hexdigest()
        assert storage_bank_card.bank_account_iban == MockIBAN


class TestGetByCardNumber:
    def test_get_by_card_number(self, bank_card_repository):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        storage_bank_card = BankCard.query.filter_by(card_number=bank_card.card_number).first()

        retrieved_bank_card = bank_card_repository.get_by_card_number(bank_card.card_number)

        assert retrieved_bank_card.expiration_date == storage_bank_card.expiration_date
        assert retrieved_bank_card._cvv_hash == storage_bank_card._cvv_hash
        assert retrieved_bank_card._pin_hash == storage_bank_card._pin_hash

    def test_for_nonexistent_bank_card(self, bank_card_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_card_repository.get_by_card_number('NonexistentCardNumber')

        assert exception_info.value.message == 'BankCard does not exist!'


class TestGetAttachedToBankAccount:
    def test_is_list_returned(self, bank_card_repository):
        bank_card_list = bank_card_repository.get_attached_to_bank_account(MockIBAN)

        assert isinstance(bank_card_list, list)

    def test_for_one_bank_card(self, bank_card_repository):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        bank_card_list = bank_card_repository.get_attached_to_bank_account(MockIBAN)

        assert bank_card.card_number in bank_card_list

    def test_for_many_bank_card(self, bank_card_repository):
        first_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)
        second_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        bank_card_list = bank_card_repository.get_attached_to_bank_account(MockIBAN)

        assert first_bank_card.card_number in bank_card_list
        assert second_bank_card.card_number in bank_card_list

    def test_for_nonexistent_bank_account(self, bank_card_repository):
        assert len(bank_card_repository.get_attached_to_bank_account(MockIBAN)) == 0


class TestDelete:
    def test_delete(self, bank_card_repository):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        bank_card_repository.delete(bank_card.card_number)

        assert BankCard.query.filter_by(card_number=bank_card.card_number).first() is None

    def test_for_nonexistent_bank_card(self, bank_card_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_card_repository.delete('NonexistentCardNumber')

        assert exception_info.value.message == 'BankCard does not exist!'


class TestBatchDelete:
    def test_for_one_bank_card(self, bank_card_repository):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        bank_card_repository.batch_delete([bank_card.card_number])

        assert BankCard.query.filter_by(card_number=bank_card.card_number).first() is None

    def test_for_many_bank_card(self, bank_card_repository):
        first_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)
        second_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, MockIBAN)

        bank_card_repository.batch_delete([first_bank_card.card_number, second_bank_card.card_number])

        assert BankCard.query.filter_by(card_number=first_bank_card.card_number).first() is None
        assert BankCard.query.filter_by(card_number=second_bank_card.card_number).first() is None
