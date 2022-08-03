import hashlib
import pytest

from app.exceptions import DoesNotExistException
from app.models.sqlalchemy.bank_card import BankCard


BANK_CARD_DATA = {
    'card_number': '4422553366447755',
    'expiration_date': '2025-05-05',
    'cvv': '111'
}


class TestCreate:
    def test_create(self, bank_card_service, bank_account, storage):
        bank_card, pin, cvv = bank_card_service.create(BANK_CARD_DATA, bank_account.IBAN)

        storage_bank_card = storage.session.query(
            BankCard.card_number
        ).filter_by(card_number=bank_card.card_number).first()

        assert storage_bank_card is not None

        assert storage_bank_card.expiration_date == BANK_CARD_DATA['expiration_date']
        assert storage_bank_card._cvv_hash == hashlib.sha256(cvv.encode('utf-8')).hexdigest()
        assert storage_bank_card._pin_hash == hashlib.sha256(pin.encode('utf-8')).hexdigest()
        assert storage_bank_card.bank_account_iban == bank_account.IBAN

    def test_with_nonexistent_bank_account(self, bank_card_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_card_service.create(BANK_CARD_DATA, 'NonexistentIBAN')

        assert exception_info.value.message == 'BankAccount does not exist!'


class TestDelete:
    def test_delete(self, bank_card_service, bank_account, storage):
        bank_card, _, _ = bank_card_service.create(BANK_CARD_DATA, bank_account.IBAN)

        bank_card_service.delete(bank_card.card_number)

        assert storage.session.query(
            BankCard.card_number
        ).filter_by(card_number=bank_card.card_number).first() is None

    def test_for_nonexistent_bank_card(self, bank_card_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_card_service.delete('NonexistentCardNumber')

        assert exception_info.value.message == 'BankCard does not exist!'


class TestDeleteBankCardsAttachedToBankAccount:
    def test_delete_with_one_bank_card_attached(self, bank_card_service, bank_account, storage):
        bank_card, _, _ = bank_card_service.create(BANK_CARD_DATA, bank_account.IBAN)

        bank_card_service.delete_bank_cards_attached_to_bank_account(bank_account.IBAN)

        assert storage.session.query(
            BankCard
        ).filter_by(card_number=bank_card.card_number).first() is None

    def test_delete_with_two_bank_cards_attached(self, bank_card_service, bank_account, storage):
        second_card_data = BANK_CARD_DATA.copy()
        second_card_data.update({'card_number': '4422553366447750'})

        bank_card, _, _ = bank_card_service.create(BANK_CARD_DATA, bank_account.IBAN)
        second_bank_card, _, _ = bank_card_service.create(second_card_data, bank_account.IBAN)

        bank_card_service.delete_bank_cards_attached_to_bank_account(bank_account.IBAN)

        assert storage.session.query(
            BankCard.card_number
        ).filter_by(card_number=bank_card.card_number).first() is None

        assert storage.session.query(
            BankCard.card_number
        ).filter_by(card_number=second_bank_card.card_number).first() is None


class TestGetByCardNumber:
    def test_retrieve(self, bank_card_service, bank_account, storage):
        bank_card, pin, cvv = bank_card_service.create(BANK_CARD_DATA, bank_account.IBAN)

        storage_bank_card = storage.session.query(
            BankCard
        ).filter_by(card_number=bank_card.card_number).first()

        retrieved_bank_card = bank_card_service.get_by_card_number(bank_card.card_number)

        assert retrieved_bank_card.expiration_date == storage_bank_card.expiration_date
        assert retrieved_bank_card._cvv_hash == storage_bank_card._cvv_hash
        assert retrieved_bank_card._pin_hash == storage_bank_card._pin_hash

        assert retrieved_bank_card._cvv_hash == hashlib.sha256(cvv.encode('utf-8')).hexdigest()
        assert retrieved_bank_card._pin_hash == hashlib.sha256(pin.encode('utf-8')).hexdigest()

    def test_retrieve_nonexistent_bank_card(self, bank_card_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_card_service.get_by_card_number('NonexistentCardNumber')

        assert exception_info.value.message == 'BankCard does not exist!'
