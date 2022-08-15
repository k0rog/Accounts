from http import HTTPStatus

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

WRONG_CUSTOMER_FIELD_TYPES = {
    'first_name': 1,
    'last_name': 1,
    'email': 1,
    'passport_number': 1,
}


def run_test_for_endpoint_with_invalid_data(client, method: str,
                                            path: str, json_data: dict, error_message: str):
    response = getattr(client, method)(path, json=json_data)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    print('=======================')
    print(response.json)
    print('=======================')
    assert 'error' in response.json

    assert response.json == error_message


class TestCustomerCreate:
    def test_new_customer(self, client, storage):
        response = client.post('/api/customers/', json=CUSTOMER_DATA)

        assert response.status_code == HTTPStatus.CREATED
        assert 'uuid' in response.json

        customer = storage.session.query(
            Customer.uuid
        ).filter_by(uuid=response.json['uuid']).first()

        assert customer is not None

        assert customer.first_name == response.json['first_name']
        assert customer.last_name == response.json['last_name']
        assert customer.email == response.json['email']
        assert customer.passport_number == response.json['passport_number']

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
        print('===================')
        print(response.json)
        print('===================')
        assert response.json['error'] == 'Customer already exist!'

    def test_each_field_with_wrong_format(self, client):
        wrong_formats = {
            'email': 'some@@@',
            'passport_number': '111'
        }

        for key, value in wrong_formats.items():
            error_message = f'{key[0].upper() + key[1:]} has wrong format!'

            wrong_data = CUSTOMER_DATA.copy()
            wrong_data[key] = wrong_formats[key]

            run_test_for_endpoint_with_invalid_data(
                client,
                'post',
                f'/api/customers/',
                wrong_data,
                error_message
            )

    def test_all_fields_with_wrong_format(self, client):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data.update({
            'email': 'some@@@',
            'passport_number': '111'
        })

        run_test_for_endpoint_with_invalid_data(
            client,
            'post',
            f'/api/customers/',
            wrong_data,
            ''
        )

    def test_each_field_with_wrong_type(self, client):
        for key, value in WRONG_CUSTOMER_FIELD_TYPES.items():
            error_message = f'{key[0].upper() + key[1:]} has wrong type!'

            wrong_data = CUSTOMER_DATA.copy()
            wrong_data[key] = WRONG_CUSTOMER_FIELD_TYPES[key]

            run_test_for_endpoint_with_invalid_data(
                client,
                'post',
                f'/api/customers/',
                wrong_data,
                error_message
            )

    def test_all_fields_with_wrong_type(self, client):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data.update(WRONG_CUSTOMER_FIELD_TYPES)

        run_test_for_endpoint_with_invalid_data(
            client,
            'post',
            f'/api/customers/',
            wrong_data,
            ''
        )


class TestCustomerUpdate:
    @staticmethod
    def generic_test_customer_update(client, storage, update_data):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.patch(
            f'/api/customers/{new_customer.json["uuid"]}',
            json=update_data
        )

        updated_customer = storage.session.query(
            Customer.uuid
        ).filter_by(uuid=new_customer.json['uuid']).first()

        assert response.status_code == HTTPStatus.NO_CONTENT

        for key, value in update_data.items():
            assert getattr(updated_customer, key) == value

    def test_one_field_customer_update(self, client, storage):
        update_data = {
            'first_name': 'George',
        }

        TestCustomerUpdate.generic_test_customer_update(client, storage, update_data)

    def test_full_customer_update(self, client, storage):
        update_data = {
            'first_name': 'George',
            'last_name': 'Kitov',
            'email': 'something@mail.com',
            'passport_number': 'HB2072131'
        }

        TestCustomerUpdate.generic_test_customer_update(client, storage, update_data)

    def test_wrong_format_for_every_field(self, client):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        update_data = {
            'email': 'some@@@',
            'passport_number': '111'
        }

        for key, value in update_data.items():
            error_message = f'{key[0].upper() + key[1:]} has wrong format!'

            run_test_for_endpoint_with_invalid_data(
                client,
                'patch',
                f'/api/customers/{new_customer.json["uuid"]}',
                {key: value},
                error_message
            )

    def test_wrong_format_for_multiply_fields(self, client):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        update_data = {
            'email': 'some@@@',
            'passport_number': '111'
        }

        run_test_for_endpoint_with_invalid_data(
            client,
            'patch',
            f'/api/customers/{new_customer.json["uuid"]}',
            update_data,
            ''
        )

    def test_wrong_field_type_for_one_field(self, client):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        for key, value in WRONG_CUSTOMER_FIELD_TYPES.items():
            error_message = f'{key[0].upper() + key[1:]} has wrong type!'

            run_test_for_endpoint_with_invalid_data(
                client,
                'patch',
                f'/api/customers/{new_customer.json["uuid"]}',
                {key: value},
                error_message
            )

    def test_wrong_field_type_for_multiply_fields(self, client):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        run_test_for_endpoint_with_invalid_data(
            client,
            'patch',
            f'/api/customers/{new_customer.json["uuid"]}',
            WRONG_CUSTOMER_FIELD_TYPES,
            ''
        )


class TestCustomerDelete:
    def test_delete_customer(self, client, storage):
        new_customer = client.post('/api/customers/', json=CUSTOMER_DATA)

        response = client.delete(f'/api/customers/{new_customer.json["uuid"]}')

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert storage.session.query(
            Customer.uuid
        ).filter_by(uuid=response.json['uuid']).first() is None

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
