from datetime import date

import pytest

from app.exceptions import DoesNotExistException, AlreadyExistException
from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.bank_card import BankCard
from app.models.sqlalchemy.many_to_many import AssociationBankAccountCustomer


BANK_ACCOUNT_DATA = {
    'currency': 'BYN',
    'balance': 100
}

BANK_CARD_DATA = {
    'expiration_date': date(2025, 5, 5),
}

MockUUID = 'MockUUID'
MockUUID2 = 'MockUUID2'


class TestCreate:
    def test_is_iban_returned(self, bank_account_service):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)

        assert hasattr(bank_account, 'IBAN')

    def test_creation(self, customer_service, bank_account_service, storage):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account is not None
        assert storage_bank_account.currency.value == BANK_ACCOUNT_DATA['currency']
        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['balance']

        assert storage.session.query(
            AssociationBankAccountCustomer
        ).filter_by(customer_id=MockUUID, bank_account_id=bank_account.IBAN).first() is not None

    def test_with_nonexistent_currency(self, bank_account_service):
        wrong_data = BANK_ACCOUNT_DATA.copy()
        wrong_data['currency'] = 'WrongData'

        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_service.create(wrong_data, MockUUID)

        assert exception_info.value.message == 'Currency does not exist!'

    def test_without_balance(self, bank_account_service, storage):
        modified_data = BANK_ACCOUNT_DATA.copy()
        del modified_data['balance']

        bank_account = bank_account_service.create(modified_data, MockUUID)

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert bank_account.balance == 0.0
        assert storage_bank_account.balance == 0.0


class TestDelete:
    def test_delete(self, bank_account_service, storage, customer, bank_card_repository):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_card, _, _ = bank_card_repository.create(BANK_CARD_DATA, bank_account.IBAN)
        card_number = bank_card.card_number[:]

        bank_account_service.delete(bank_account.IBAN)

        assert storage.session.query(
            BankAccount.IBAN
        ).filter_by(IBAN=bank_account.IBAN).first() is None

        assert storage.session.query(
            BankCard.card_number
        ).filter_by(card_number=card_number).first() is None

        assert storage.session.query(
            AssociationBankAccountCustomer.bank_account_id
        ).filter_by(bank_account_id=bank_account.IBAN).first() is None

    def test_for_nonexistent_bank_account(self, bank_account_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_service.delete('NonExistentIBAN')

        assert exception_info.value.message == 'BankAccount does not exist!'


class TestOwnedByCustomerBankAccountsDelete:
    @staticmethod
    def perform_after_delete_assertions(storage, iban: str, customer_uuid: str):
        assert storage.session.query(
            BankAccount.IBAN
        ).filter_by(IBAN=iban).first() is None

        assert storage.session.query(
            AssociationBankAccountCustomer
        ).filter_by(customer_id=customer_uuid, bank_account_id=iban).first() is None

    def test_for_one_bank_account_owned_by_customer(self, bank_account_service, storage):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)
        
        bank_account_service.delete_owned_by_customer_bank_accounts(MockUUID)

        self.perform_after_delete_assertions(storage, bank_account.IBAN, MockUUID)

    def test_for_many_bank_accounts_owned_by_customer(self, bank_account_service, storage):
        first_bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)
        second_bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_service.delete_owned_by_customer_bank_accounts(MockUUID)

        self.perform_after_delete_assertions(storage, first_bank_account.IBAN, MockUUID)
        self.perform_after_delete_assertions(storage, second_bank_account.IBAN, MockUUID)


class TestAddBankAccountForCustomer:
    def test_add_bank_account_for_customer(self, bank_account_service, storage):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_service.add_bank_account_for_customer(bank_account.IBAN, MockUUID2)

        assert storage.session.query(
            AssociationBankAccountCustomer
        ).filter_by(customer_id=MockUUID2, bank_account_id=bank_account.IBAN).first() is not None

    def test_add_nonexistent_bank_account(self, bank_account_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_service.add_bank_account_for_customer('NonexistentIBAN', MockUUID2)

        assert exception_info.value.message == 'BankAccount does not exist!'

    def test_duplicated_assign(self, bank_account_service):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)

        with pytest.raises(AlreadyExistException) as exception_info:
            bank_account_service.add_bank_account_for_customer(bank_account.IBAN, MockUUID)

        assert exception_info.value.message == 'Relation already exist!'


class TestUpdateByAmount:
    def test_increase(self, bank_account_service, storage):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)
        amount = 50

        bank_account_service.update_balance_by_amount(bank_account.IBAN, amount)

        assert bank_account.balance == BANK_ACCOUNT_DATA['balance'] + amount

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['balance'] + amount

    def test_decrease(self, bank_account_service, storage):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)
        amount = -50

        bank_account_service.update_balance_by_amount(bank_account.IBAN, amount)

        assert bank_account.balance == BANK_ACCOUNT_DATA['balance'] + amount

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['balance'] + amount


class TestGetByIBAN:
    def test_retrieve(self, bank_account_service):
        new_bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account = bank_account_service.get_by_iban(new_bank_account.IBAN)

        assert bank_account.IBAN == new_bank_account.IBAN
        assert bank_account.balance == BANK_ACCOUNT_DATA['balance']
        assert bank_account.currency.value == BANK_ACCOUNT_DATA['currency']

    def test_for_nonexistent_bank_account(self, bank_account_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_service.get_by_iban('NonExistentIBAN')

        assert exception_info.value.message == 'BankAccount does not exist!'
