import pytest

from app.exceptions import AlreadyExistException, DoesNotExistException
from app.models.sqlalchemy.customer import Customer


CUSTOMER_DATA = {
    'first_name': 'John',
    'last_name': 'Smith',
    'email': 'jsmith@gmail.com',
    'passport_number': 'HB1111111',
}


class TestCreate:
    def test_is_uuid_returned(self, customer_repository):
        customer = customer_repository.create(CUSTOMER_DATA)

        assert hasattr(customer, 'uuid')

    def test_create(self, customer_repository, storage):
        customer = customer_repository.create(CUSTOMER_DATA)

        storage_customer = Customer.query.filter_by(uuid=customer.uuid).first()

        assert storage_customer is not None

        assert storage_customer.first_name == CUSTOMER_DATA['first_name']
        assert storage_customer.last_name == CUSTOMER_DATA['last_name']
        assert storage_customer.email == CUSTOMER_DATA['email']
        assert storage_customer.passport_number == CUSTOMER_DATA['passport_number']

    def test_for_duplicated_passport_number(self, customer_repository):
        customer_repository.create(CUSTOMER_DATA)

        with pytest.raises(AlreadyExistException) as exception_info:
            customer_repository.create(CUSTOMER_DATA)

        assert exception_info.value.message == 'Customer already exist!'


class TestIsExists:
    def test_is_exists_true(self, customer_repository):
        customer = customer_repository.create(CUSTOMER_DATA)

        assert customer_repository.is_exists(customer.uuid)

    def test_is_exists_false(self, customer_repository):
        assert not customer_repository.is_exists('NonexistentUUID')


class TestUpdate:
    def test_for_one_field(self, customer_repository):
        customer = customer_repository.create(CUSTOMER_DATA)

        update_data = {
            'first_name': 'Bob'
        }

        customer_repository.update(customer.uuid, update_data)

        storage_customer = Customer.query.filter_by(uuid=customer.uuid).first()

        assert storage_customer.first_name == update_data['first_name']

    def test_for_many_fields(self, customer_repository):
        customer = customer_repository.create(CUSTOMER_DATA)

        update_data = {
            'first_name': 'Bob',
            'last_name': 'Miller'
        }

        customer_repository.update(customer.uuid, update_data)

        storage_customer = Customer.query.filter_by(uuid=customer.uuid).first()

        assert storage_customer.first_name == update_data['first_name']
        assert storage_customer.last_name == update_data['last_name']

    def test_for_duplicated_passport_number(self, customer_repository):
        customer_repository.create(CUSTOMER_DATA)

        second_customer_data = CUSTOMER_DATA.copy()
        second_customer_data.update({'passport_number': 'HB1111112'})

        second_customer = customer_repository.create(CUSTOMER_DATA)

        update_data = {
            'passport_number': CUSTOMER_DATA['passport_number']
        }

        with pytest.raises(AlreadyExistException) as exception_info:
            customer_repository.update(second_customer.uuid, update_data)

        assert exception_info.value.message == 'Customer already exist!'

    def test_for_nonexistent_customer(self, customer_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            customer_repository.update('NonexistentUUID', {'first_name': 'Bob'})

        assert exception_info.value.message == 'Customer does not exist!'


class TestDelete:
    def test_delete(self, customer_repository):
        customer = customer_repository.create(CUSTOMER_DATA)

        customer_repository.delete(customer.uuid)

        assert Customer.query.filter_by(uuid=customer.uuid).first() is None

    def test_for_nonexistent_customer(self, customer_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            customer_repository.delete('NonexistentUUID')

        assert exception_info.value.message == 'Customer does not exist!'


class TestGetByUUID:
    def test_get_by_uuid(self, customer_repository):
        customer = customer_repository.create(CUSTOMER_DATA)

        retrieved_customer = customer_repository.get_by_uuid(customer.uuid)

        storage_customer = Customer.query.filter_by(uuid=customer.uuid).first()

        assert storage_customer.first_name == retrieved_customer.first_name
        assert storage_customer.last_name == retrieved_customer.last_name
        assert storage_customer.email == retrieved_customer.email
        assert storage_customer.passport_number == retrieved_customer.passport_number

    def test_for_nonexistent_customer(self, customer_repository):
        with pytest.raises(DoesNotExistException) as exception_info:
            customer_repository.get_by_uuid('NonexistentUUID')

        assert exception_info.value.message == 'Customer does not exist!'
