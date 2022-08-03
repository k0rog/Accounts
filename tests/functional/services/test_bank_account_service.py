import pytest

from app.exceptions import DoesNotExistException
from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.bank_card import BankCard
from app.models.sqlalchemy.many_to_many import bank_accounts


BANK_ACCOUNT_DATA = {
    'currency': 'BYN',
    'balance': 100
}


class TestCreate:
    def test_is_iban_returned(self, bank_account_service, customer):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)

        assert hasattr(bank_account, 'IBAN')

    def test_creation(self, customer_service, bank_account_service, storage, customer):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account is not None
        assert storage_bank_account.currency == BANK_ACCOUNT_DATA['currency']
        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['currency']

        assert storage.session.query(
            bank_accounts
        ).filter_by(customer_id=customer.uuid, bank_account_id=bank_account.IBAN).first() is not None

    def test_with_nonexistent_currency(self, bank_account_service, customer):
        wrong_data = BANK_ACCOUNT_DATA.copy()
        wrong_data['currency'] = 'WrongData'

        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_service.create(wrong_data, customer.uuid)

        assert exception_info.value.message == 'Currency does not exist!'

    def test_without_balance(self, bank_account_service, storage, customer):
        modified_data = BANK_ACCOUNT_DATA.copy()
        del modified_data['balance']

        bank_account = bank_account_service.create(modified_data, customer.uuid)

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert bank_account.balance == 0.0
        assert storage_bank_account.balance == 0.0


class TestDelete:
    def test_delete(self, bank_account_service, storage, customer, bank_card):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)

        bank_card.bank_account_iban = bank_account.IBAN
        storage.session.commit()

        bank_account_service.delete(bank_account.IBAN)

        assert storage.session.query(
            BankAccount.IBAN
        ).filter_by(IBAN=bank_account.IBAN).first() is None

        assert storage.session.query(
            BankCard.card_number
        ).filter_by(card_number=bank_card.card_number).first() is None

        assert storage.session.query(
            bank_accounts.bank_account_id
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
            bank_accounts
        ).filter_by(customer_id=customer_uuid, bank_account_id=iban).first() is None

    def test_for_one_bank_account_owned_by_customer(self, bank_account_service, storage, customer):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)
        
        bank_account_service.delete_owned_by_customer_bank_accounts(customer.uuid)

        self.perform_after_delete_assertions(storage, bank_account.IBAN, customer.uuid)

    def test_for_many_bank_accounts_owned_by_customer(self, bank_account_service, storage, customer):
        first_bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)
        second_bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)

        bank_account_service.delete_owned_by_customer_bank_accounts(customer.uuid)

        self.perform_after_delete_assertions(storage, first_bank_account.IBAN, customer.uuid)
        self.perform_after_delete_assertions(storage, second_bank_account.IBAN, customer.uuid)


class TestAddBankAccountForCustomer:
    def test_add_bank_account_for_customer(self, bank_account_service, storage, customer):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)

        bank_account_service.add_bank_account_for_customer(customer.uuid, bank_account.IBAN)

        assert storage.session.query(
            bank_accounts
        ).filter_by(customer_id=customer.uuid, bank_account_id=bank_account.IBAN).first() is not None

    def test_add_nonexistent_bank_account(self, bank_account_service, storage, customer):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_service.add_bank_account_for_customer(customer.uuid, 'NonexistentIBAN')

        assert exception_info.value.message == 'BankAccount does not exist!'


class TestUpdateByAmount:
    def test_increase(self, bank_account_service, storage, customer):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)
        amount = 50

        bank_account = bank_account_service.update_balance_by_amount(bank_account.IBAN, amount)

        assert bank_account.balance == BANK_ACCOUNT_DATA['balance'] + amount

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['balance'] + amount

    def test_decrease(self, bank_account_service, storage, customer):
        bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)
        amount = -50

        bank_account = bank_account_service.update_balance_by_amount(bank_account.IBAN, amount)

        assert bank_account.balance == BANK_ACCOUNT_DATA['balance'] - amount

        storage_bank_account = storage.session.query(
            BankAccount
        ).filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['balance'] - amount


class TestGetByIBAN:
    def test_retrieve(self, bank_account_service, customer):
        new_bank_account = bank_account_service.create(BANK_ACCOUNT_DATA, customer.uuid)

        bank_account = bank_account_service.get_by_iban(new_bank_account.IBAN)

        assert bank_account.IBAN == new_bank_account.IBAN
        assert bank_account.balance == BANK_ACCOUNT_DATA['balance']
        assert bank_account.currency == BANK_ACCOUNT_DATA['currency']

    def test_for_nonexistent_bank_account(self, bank_account_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_service.get_by_uuid('NonExistentIBAN')

        assert exception_info.value.message == 'BankAccount does not exist!'
