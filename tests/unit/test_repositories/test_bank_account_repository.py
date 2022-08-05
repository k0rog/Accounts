import pytest

from app.exceptions import DoesNotExistException, AlreadyExistException
from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.many_to_many import bank_accounts


BANK_ACCOUNT_DATA = {
    'currency': 'BYN',
    'balance': 100
}

MockUUID = 'MockUUID'
MockUUID2 = 'MockUUID2'


class TestCreate:
    def test_has_iban(self, bank_account_repository):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        assert hasattr(bank_account, 'IBAN')

    def test_is_many_to_many_row_created(self, bank_account_repository, storage):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        assert storage.session.query(
            bank_accounts
        ).filter_by(bank_account_id=bank_account.IBAN, customer_id=MockUUID).first() is not None
        
    def test_create_with_balance(self, bank_account_repository):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        storage_bank_account = BankAccount.query.filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account is not None

        assert storage_bank_account.currency == BANK_ACCOUNT_DATA['currency']
        assert storage_bank_account.balance == float(BANK_ACCOUNT_DATA['balance'])

    def test_create_without_balance(self, bank_account_repository, customer):
        bank_account_data = {
            'currency': 'BYN'
        }

        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        storage_bank_account = BankAccount.query.filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account is not None

        assert storage_bank_account.currency == bank_account_data['currency']
        assert storage_bank_account.balance == 0.0

    def test_with_nonexistent_currency(self, bank_account_repository):
        bank_account_data = {
            'currency': 'NonexistentCurrency'
        }

        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_repository.create(bank_account_data, MockUUID)

        assert exception_info.value.message == 'Currency does not exist!'


class TestGetByIban:
    def test_get_by_iban(self, bank_account_repository):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        retrieved_bank_account = bank_account_repository.get_by_iban(bank_account.IBAN)

        storage_bank_account = BankAccount.query.filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account.balance == retrieved_bank_account.balance
        assert storage_bank_account.currency == retrieved_bank_account.currency

    def test_for_nonexistent_bank_account(self, bank_account_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_repository.get_by_iban('NonexistentIBAN')

        assert exception_info.value.message == 'BankAccount does not exist!'


class TestDelete:
    def test_delete(self, bank_account_repository, storage):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_repository.delete(bank_account.IBAN)

        assert BankAccount.query.filter_by(IBAN=bank_account.IBAN).first() is None

        assert storage.session.query(
            bank_accounts.bank_account_id
        ).filter_by(bank_account_id=bank_account.IBAN).first() is None

    def test_for_nonexistent_bank_account(self, bank_account_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_repository.delete('NonexistentIBAN')

        assert exception_info.value.message == 'BankAccount does not exist!'


class TestUpdateBalanceByAmount:
    def test_for_positive_amount(self, bank_account_repository, storage):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)
        amount = 50

        bank_account_repository.update_balance_by_amount(bank_account.IBAN, amount)

        storage_bank_account = BankAccount.query.filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['balance'] + amount

    def test_for_negative_amount(self, bank_account_repository, storage):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)
        amount = -50

        bank_account_repository.update_balance_by_amount(bank_account.IBAN, amount)

        storage_bank_account = BankAccount.query.filter_by(IBAN=bank_account.IBAN).first()

        assert storage_bank_account.balance == BANK_ACCOUNT_DATA['balance'] - amount


class TestGetBankAccountsOwnedByCustomer:
    def test_for_one_bank_account(self, bank_account_repository):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_list = bank_account_repository.get_owned_by_customer(MockUUID)

        assert bank_account.IBAN in bank_account_list

    def test_for_many_bank_accounts(self, bank_account_repository):
        first_bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)
        second_bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_list = bank_account_repository.get_owned_by_customer(MockUUID)

        assert first_bank_account.IBAN in bank_account_list
        assert second_bank_account.IBAN in bank_account_list

    def test_for_nonexistent_customer(self, bank_account_repository):
        assert len(bank_account_repository.get_owned_by_customer(MockUUID)) == 0


class TestBatchDelete:
    def test_for_one_bank_account(self, bank_account_repository, storage):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_repository.batch_delete([bank_account.IBAN])

        assert BankAccount.query.filter_by(IBAN=bank_account.IBAN).first() is None

        assert storage.session.query(
            bank_accounts.bank_account_id
        ).filter_by(bank_account_id=bank_account.IBAN).first() is None

    def test_for_many_bank_accounts(self, bank_account_repository, storage):
        first_bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)
        second_bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_repository.batch_delete(
            ibans=[first_bank_account.IBAN, second_bank_account.IBAN]
        )

        assert BankAccount.query.filter_by(IBAN=first_bank_account.IBAN).first() is None

        assert storage.session.query(
            bank_accounts.bank_account_id
        ).filter_by(bank_account_id=first_bank_account.IBAN).first() is None

        assert BankAccount.query.filter_by(IBAN=second_bank_account.IBAN).first() is None

        assert storage.session.query(
            bank_accounts.bank_account_id
        ).filter_by(bank_account_id=second_bank_account.IBAN).first() is None


class TestAssignToCustomer:
    def test_assign(self, bank_account_repository, storage):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        bank_account_repository.assign_to_customer(bank_account.IBAN, MockUUID2)

        assert storage.session.query(
            bank_accounts.bank_account_id
        ).filter_by(bank_account_id=bank_account.IBAN, customer_id=MockUUID2).first() is not None

    def test_duplicated_assign(self, bank_account_repository, storage):
        bank_account = bank_account_repository.create(BANK_ACCOUNT_DATA, MockUUID)

        with pytest.raises(AlreadyExistException) as exception_info:
            bank_account_repository.assign_to_customer(bank_account.IBAN, MockUUID)

        assert exception_info.value.message == 'Relation already exist!'

    def test_for_nonexistent_bank_account(self, bank_account_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            bank_account_repository.assign_to_customer('NonexistentIBAN', MockUUID)

        assert exception_info.value.message == 'BankAccount does not exist!'
