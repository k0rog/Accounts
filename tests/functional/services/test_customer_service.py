import pytest

from app.exceptions import ValidationException, AlreadyExistException, DoesNotExistException
from app.models.sqlalchemy.customer import Customer
from app.models.sqlalchemy.many_to_many import bank_accounts


CUSTOMER_DATA = {
    'first_name': 'Ilya',
    'last_name': 'Auramenka',
    'email': 'avramneoko6@gmail.com',
    'passport_number': 'HB2072131',
    'bank_account': {
        'currency': 'BYN'
    }
}


class TestCreate:
    def test_is_uuid_returned(self, customer_service):
        customer = customer_service.create_customer(CUSTOMER_DATA)

        assert 'uuid' in customer

    def test_customer_creation(self, customer_service, storage):
        customer = customer_service.create_customer(CUSTOMER_DATA)

        storage_customer = storage.session.query(
            Customer.uuid
        ).filter_by(uuid=customer['uuid']).first()

        storage_bank_account = storage.session.query(
            bank_accounts
        ).filter_by(customer_id=customer['uuid']).first()

        assert storage_customer is not None
        assert storage_bank_account is not None

        assert storage_customer.first_name == CUSTOMER_DATA['first_name']
        assert storage_customer.last_name == CUSTOMER_DATA['last_name']
        assert storage_customer.email == CUSTOMER_DATA['email']
        assert storage_customer.passport_number == CUSTOMER_DATA['passport_number']

        assert storage_bank_account.balance == CUSTOMER_DATA['bank_account']['balance']
        assert storage_bank_account.currency == CUSTOMER_DATA['bank_account']['currency']

    def test_with_duplicated_passport_number(self, customer_service):
        customer_service.create_customer(CUSTOMER_DATA)

        with pytest.raises(AlreadyExistException) as exception_info:
            customer_service.create_customer(CUSTOMER_DATA)

        assert exception_info.value.message == 'Customer already exist!'


class TestUpdate:
    def test_one_field_update(self, customer_service, storage):
        new_customer = customer_service.create_customer(CUSTOMER_DATA)

        update_data = {
            'passport_number': 'HB212072131'
        }

        customer_service.update_customer(new_customer['uuid'], update_data)

        customer = storage.session.query(
            Customer
        ).filter_by(uuid=new_customer['uuid']).first()

        assert customer.passport_number == update_data['passport_number']

    def test_multiple_field_update(self, customer_service, storage):
        new_customer = customer_service.create_customer(CUSTOMER_DATA)

        update_data = {
            'passport_number': 'HB212072131',
            'first_name': 'George',
            'last_name': 'kitov'
        }

        customer_service.update_customer(new_customer['uuid'], update_data)

        customer = storage.session.query(
            Customer
        ).filter_by(uuid=new_customer['uuid']).first()

        assert customer.passport_number == update_data['passport_number']
        assert customer.first_name == update_data['first_name']
        assert customer.last_name == update_data['last_name']

    def test_with_wrong_passport_number_format(self, customer_service):
        new_customer = customer_service.create_customer(CUSTOMER_DATA)

        update_data = {
            'passport_number': 'WRONGNUMBER',
        }

        with pytest.raises(ValidationException) as exception_info:
            customer_service.update_customer(new_customer['uuid'], update_data)

        assert exception_info.value.message == 'Wrong format for passport_number field!'

    def test_with_wrong_email_format(self, customer_service):
        new_customer = customer_service.create_customer(CUSTOMER_DATA)

        update_data = {
            'email': 'WRONGEMAIL',
        }

        with pytest.raises(ValidationException) as exception_info:
            customer_service.update_customer(new_customer['uuid'], update_data)

        assert exception_info.value.message == 'Wrong format for email field!'


class TestDelete:
    def test_delete_customer(self, customer_service, storage):
        new_customer = customer_service.create_customer(CUSTOMER_DATA)

        customer_service.delete_customer(new_customer['uuid'])

        assert storage.session.query(
            Customer
        ).filter_by(uuid=new_customer['uuid']).first() is None

    def test_delete_nonexistent_customer(self, customer_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            customer_service.delete_customer('NonExistentUUID')

        assert exception_info.value.message == 'Customer does not exist!'


class TestGetByUUID:
    def test_retrieve_customer(self, customer_service):
        new_customer = customer_service.create_customer(CUSTOMER_DATA)

        customer = customer_service.get_customer(new_customer['uuid'])

        assert customer['first_name'] == CUSTOMER_DATA['first_name']
        assert customer['last_name'] == CUSTOMER_DATA['last_name']
        assert customer['email'] == CUSTOMER_DATA['email']
        assert customer['passport_number'] == CUSTOMER_DATA['passport_number']

    def test_delete_nonexistent_customer(self, customer_service):
        with pytest.raises(DoesNotExistException) as exception_info:
            customer_service.get_customer('NonExistentUUID')

        assert exception_info.value.message == 'Customer does not exist!'
