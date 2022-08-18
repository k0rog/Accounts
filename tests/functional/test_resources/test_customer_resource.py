import re
from http import HTTPStatus

import pytest

from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.customer import Customer
from app.models.sqlalchemy.many_to_many import AssociationBankAccountCustomer

CUSTOMER_DATA = {
    'first_name': 'Ilya',
    'last_name': 'Auramenka',
    'email': 'avramneoko6@gmail.com',
    'passport_number': 'HB2072131',
    'bank_account': {
        'currency': 'BYN'
    }
}


class TestCustomerCreate:
    def test_uuid_returned(self, client):
        response = client.post('/api/customers/', json=CUSTOMER_DATA)

        assert response.status_code == HTTPStatus.CREATED
        assert 'uuid' in response.json

        assert re.match(
            r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z',
            response.json['uuid'],
            flags=re.I
        ) is not None

    def test_new_customer(self, client, storage):
        response = client.post('/api/customers/', json=CUSTOMER_DATA)

        assert response.status_code == HTTPStatus.CREATED

        customer = storage.session.query(
            Customer
        ).filter_by(uuid=response.json['uuid']).first()

        assert customer is not None

        bank_account = storage.session \
            .query(BankAccount) \
            .join(AssociationBankAccountCustomer) \
            .filter(AssociationBankAccountCustomer.customer_id == response.json['uuid']).first()

        assert bank_account is not None

        assert bank_account.currency.value == CUSTOMER_DATA['bank_account']['currency']

    def test_duplicated_passport_number_new_customer(self, client):
        client.post('/api/customers/', json=CUSTOMER_DATA)
        response = client.post('/api/customers/', json=CUSTOMER_DATA)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'error' in response.json
        assert response.json['error'] == 'Customer already exist!'

    @pytest.mark.parametrize('field,value', (('email', 'some@@@'), ('passport_number', '111')))
    def test_with_wrong_field_format(self, client, field, value):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data[field] = value

        response = client.post('/api/customers/', json=wrong_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        assert response.json['errors'][field][0] == f'Not a valid {field} format.'

    def test_with_all_fields_having_wrong_format(self, client):
        wrong_data = {
            'email': 'some@@@',
            'passport_number': '111'
        }
        customer_data = CUSTOMER_DATA.copy()
        customer_data.update(wrong_data)

        response = client.post('/api/customers/', json=wrong_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        for key in wrong_data.keys():
            assert response.json['errors'][key][0] == f'Not a valid {key} format.'

    @pytest.mark.parametrize('field', ('first_name', 'last_name', 'email', 'passport_number'))
    @pytest.mark.parametrize('value', (1,))
    def test_with_wrong_field_type(self, client, field, value):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data[field] = value

        response = client.post('/api/customers/', json=wrong_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        assert response.json['errors'][field][0] == f'Not a valid string.'

    def test_with_all_fields_having_wrong_type(self, client):
        wrong_data = {
            'first_name': 1,
            'last_name': 1,
            'email': 1,
            'passport_number': 1,
            'bank_account': {
                'currency': 1
            }
        }

        response = client.post('/api/customers/', json=wrong_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        assert response.json['errors']['first_name'][0] == f'Not a valid string.'
        assert response.json['errors']['last_name'][0] == f'Not a valid string.'
        assert response.json['errors']['email'][0] == f'Not a valid string.'
        assert response.json['errors']['passport_number'][0] == f'Not a valid string.'
        assert response.json['errors']['bank_account']['currency'][0] == f'Not a valid string.'


class TestCustomerUpdate:
    def test_one_field_customer_update(self, client, storage):
        update_data = {
            'first_name': 'George',
        }

        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.patch(
            f'/api/customers/{new_customer.json["uuid"]}',
            json=update_data
        )

        updated_customer = storage.session.query(
            Customer
        ).filter_by(uuid=new_customer.json['uuid']).first()

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert updated_customer.first_name == update_data['first_name']

    def test_full_customer_update(self, client, storage):
        update_data = {
            'first_name': 'George',
            'last_name': 'Kitov',
            'email': 'something@mail.com',
            'passport_number': 'HB2072131'
        }

        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.patch(
            f'/api/customers/{new_customer.json["uuid"]}',
            json=update_data
        )

        updated_customer = storage.session.query(
            Customer
        ).filter_by(uuid=new_customer.json['uuid']).first()

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert updated_customer.first_name == update_data['first_name']
        assert updated_customer.last_name == update_data['last_name']
        assert updated_customer.email == update_data['email']
        assert updated_customer.passport_number == update_data['passport_number']

    @pytest.mark.parametrize('field,value', (('email', 'some@@@'), ('passport_number', '111')))
    def test_with_wrong_field_format(self, client, field, value):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.patch(f'/api/customers/{new_customer.json["uuid"]}', json={field: value})

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        assert response.json['errors'][field][0] == f'Not a valid {field} format.'

    def test_with_all_fields_having_wrong_format(self, client):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        update_data = {
            'email': 'some@@@',
            'passport_number': '111'
        }

        response = client.patch(f'/api/customers/{new_customer.json["uuid"]}', json=update_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        for key in update_data.keys():
            assert response.json['errors'][key][0] == f'Not a valid {key} format.'

    @pytest.mark.parametrize('field', ('first_name', 'last_name', 'email', 'passport_number'))
    @pytest.mark.parametrize('value', (1,))
    def test_with_wrong_field_type(self, client, field, value):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.patch(f'/api/customers/{new_customer.json["uuid"]}', json={field: value})

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        assert response.json['errors'][field][0] == f'Not a valid string.'

    def test_with_all_fields_having_wrong_type(self, client):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.patch(
            f'/api/customers/{new_customer.json["uuid"]}',
            json={
                'first_name': 1,
                'last_name': 1,
                'email': 1,
                'passport_number': 1,
            })

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert 'errors' in response.json

        assert response.json['errors']['first_name'][0] == f'Not a valid string.'
        assert response.json['errors']['last_name'][0] == f'Not a valid string.'
        assert response.json['errors']['email'][0] == f'Not a valid string.'
        assert response.json['errors']['passport_number'][0] == f'Not a valid string.'


class TestCustomerDelete:
    def test_delete_customer(self, client, storage):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.delete(f'/api/customers/{new_customer.json["uuid"]}')

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert storage.session.query(
            Customer.uuid
        ).filter_by(uuid=new_customer.json['uuid']).first() is None

    def test_delete_nonexistent_customer(self, client, customer_repository):
        response = client.delete(f'/api/customers/something')

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'error' in response.json
        assert response.json['error'] == 'Customer does not exist!'


class TestCustomerRetrieve:
    def test_customer_retrieve(self, client, customer_repository):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.get(f'/api/customers/{new_customer.json["uuid"]}')

        assert response.status_code == HTTPStatus.OK
        assert CUSTOMER_DATA['first_name'] == response.json['first_name']
        assert CUSTOMER_DATA['last_name'] == response.json['last_name']
        assert CUSTOMER_DATA['passport_number'] == response.json['passport_number']
        assert CUSTOMER_DATA['email'] == response.json['email']
