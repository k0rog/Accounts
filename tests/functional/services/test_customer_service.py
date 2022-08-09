import pytest

from app.exceptions import AlreadyExistException, DoesNotExistException
from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.customer import Customer
from app.models.sqlalchemy.many_to_many import association_account_customer


CUSTOMER_DATA = {
    'first_name': 'John',
    'last_name': 'Smith',
    'email': 'jsmit@gmail.com',
    'passport_number': 'HB1111111',
    'bank_account': {
        'currency': 'BYN'
    }
}


class TestCreate:
    def test_is_uuid_returned(self, customer_service):
        customer = customer_service.create(CUSTOMER_DATA)

        assert hasattr(customer, 'uuid')

    def test_customer_creation(self, customer_service, storage):
        customer = customer_service.create(CUSTOMER_DATA)

        storage_customer = storage.session.query(
            Customer
        ).filter_by(uuid=customer.uuid).first()

        storage_bank_account = storage.session\
            .query(BankAccount)\
            .join(association_account_customer, Customer)\
            .filter(Customer.uuid == customer.uuid).first()

        assert storage_customer is not None
        assert storage_bank_account is not None

        assert storage_customer.first_name == CUSTOMER_DATA['first_name']
        assert storage_customer.last_name == CUSTOMER_DATA['last_name']
        assert storage_customer.email == CUSTOMER_DATA['email']
        assert storage_customer.passport_number == CUSTOMER_DATA['passport_number']

        assert storage_bank_account.currency.value == CUSTOMER_DATA['bank_account']['currency']

    def test_with_duplicated_passport_number(self, customer_service):
        customer_service.create(CUSTOMER_DATA)

        with pytest.raises(AlreadyExistException) as exception_info:
            customer_service.create(CUSTOMER_DATA)

        assert exception_info.value.message == 'Customer already exist!'


class TestUpdate:
    def test_one_field_update(self, customer_service, storage):
        new_customer = customer_service.create(CUSTOMER_DATA)

        update_data = {
            'passport_number': 'HB1111112'
        }

        customer_service.update(new_customer.uuid, update_data)

        customer = storage.session.query(
            Customer
        ).filter_by(uuid=new_customer.uuid).first()

        assert customer.passport_number == update_data['passport_number']

    def test_multiple_field_update(self, customer_service, storage):
        new_customer = customer_service.create(CUSTOMER_DATA)

        update_data = {
            'passport_number': 'HB1111112',
            'first_name': 'Jack',
            'last_name': 'Miller'
        }

        customer_service.update(new_customer.uuid, update_data)

        customer = storage.session.query(
            Customer
        ).filter_by(uuid=new_customer.uuid).first()

        assert customer.passport_number == update_data['passport_number']
        assert customer.first_name == update_data['first_name']
        assert customer.last_name == update_data['last_name']

    def test_passport_number_update_to_already_existent(self, customer_service):
        customer_service.create(CUSTOMER_DATA)

        second_customer_data = CUSTOMER_DATA.copy()
        second_customer_data.update({'passport_number': 'HB1111112'})

        second_customer = customer_service.create(second_customer_data)

        update_data = {
            'passport_number': 'HB1111111'
        }

        with pytest.raises(AlreadyExistException) as exception_info:
            customer_service.update(second_customer.uuid, update_data)

        assert exception_info.value.message == 'Customer already exist!'


class TestDelete:
    def test_delete_customer(self, customer_service, storage):
        new_customer = customer_service.create(CUSTOMER_DATA)

        customer_service.delete(new_customer.uuid)

        assert storage.session.query(
            Customer
        ).filter_by(uuid=new_customer.uuid).first() is None

    def test_delete_nonexistent_customer(self, customer_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            customer_service.delete('NonExistentUUID')

        assert exception_info.value.message == 'Customer does not exist!'


class TestGetByUUID:
    def test_retrieve_customer(self, customer_service):
        new_customer = customer_service.create(CUSTOMER_DATA)

        customer = customer_service.get_by_uuid(new_customer.uuid)

        assert customer.first_name == CUSTOMER_DATA['first_name']
        assert customer.last_name == CUSTOMER_DATA['last_name']
        assert customer.email == CUSTOMER_DATA['email']
        assert customer.passport_number == CUSTOMER_DATA['passport_number']

    def test_for_nonexistent_customer(self, customer_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            customer_service.get_by_uuid('NonExistentUUID')

        assert exception_info.value.message == 'Customer does not exist!'
