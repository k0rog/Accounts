from datetime import date

import pytest

from app.exceptions import DoesNotExistException
from app.models.sqlalchemy.bank_card import BankCard


BANK_CARD_DATA = {
    'expiration_date': date(2025, 5, 5),
}


class TestCreate:
    def test_has_card_number(self, bank_card_repository, bank_account):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        assert hasattr(bank_card, 'card_number')

    def test_create(self, bank_card_repository, storage, bank_account):
        bank_card, pin, cvv = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        storage_bank_card = storage.session.query(
            BankCard
        ).filter_by(card_number=bank_card.card_number).first()

        assert storage_bank_card is not None

        assert storage_bank_card.expiration_date == BANK_CARD_DATA['expiration_date']
        assert bank_card.check_cvv(cvv)
        assert bank_card.check_pin(pin)
        assert storage_bank_card.bank_account_iban == bank_account.IBAN


class TestGetByCardNumber:
    def test_get_by_card_number(self, bank_card_repository, bank_account, storage):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        storage_bank_card = storage.session.query(
            BankCard
        ).filter_by(card_number=bank_card.card_number).first()

        retrieved_bank_card = bank_card_repository.get_by_card_number(bank_card.card_number)

        assert retrieved_bank_card.expiration_date == storage_bank_card.expiration_date
        assert retrieved_bank_card._cvv_hash == storage_bank_card._cvv_hash
        assert retrieved_bank_card._pin_hash == storage_bank_card._pin_hash

    def test_for_nonexistent_bank_card(self, bank_card_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_card_repository.get_by_card_number('NonexistentCardNumber')

        assert exception_info.value.message == 'BankCard does not exist!'


class TestGetAttachedToBankAccount:
    def test_is_list_returned(self, bank_card_repository, bank_account):
        bank_card_list = bank_card_repository.get_attached_to_bank_account(bank_account.IBAN)

        assert isinstance(bank_card_list, list)

    def test_for_one_bank_card(self, bank_card_repository, bank_account):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        bank_card_list = bank_card_repository.get_attached_to_bank_account(bank_account.IBAN)

        assert bank_card.card_number in bank_card_list

    def test_for_many_bank_card(self, bank_card_repository, bank_account):
        first_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)
        second_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        bank_card_list = bank_card_repository.get_attached_to_bank_account(bank_account.IBAN)

        assert first_bank_card.card_number in bank_card_list
        assert second_bank_card.card_number in bank_card_list

    def test_for_nonexistent_bank_account(self, bank_card_repository, bank_account):
        assert len(bank_card_repository.get_attached_to_bank_account(bank_account.IBAN)) == 0


class TestDelete:
    def test_delete(self, bank_card_repository, bank_account, storage):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        is_deleted = bank_card_repository.delete(bank_card.card_number)

        assert is_deleted

        assert storage.session.query(
            BankCard
        ).filter_by(card_number=bank_card.card_number).first() is None

    def test_for_nonexistent_bank_card(self, bank_card_repository):
        is_deleted = bank_card_repository.delete('NonexistentBankCard')

        assert not is_deleted


class TestBulkDelete:
    def test_for_one_bank_card(self, bank_card_repository, bank_account, storage):
        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        bank_card_repository.bulk_delete([bank_card.card_number])

        assert storage.session.query(
            BankCard
        ).filter_by(card_number=bank_card.card_number).first() is None

    def test_for_many_bank_card(self, bank_card_repository, bank_account, storage):
        first_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)
        second_bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)

        bank_card_repository.bulk_delete([first_bank_card.card_number, second_bank_card.card_number])

        assert storage.session.query(
            BankCard
        ).filter_by(card_number=first_bank_card.card_number).first() is None

        assert storage.session.query(
            BankCard
        ).filter_by(card_number=second_bank_card.card_number).first() is None
