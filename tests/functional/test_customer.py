from http import HTTPStatus


class TestNewCustomer:
    CUSTOMER_DATA = {
        'first_name': 'Ilya',
        'last_name': 'Auramenka',
        'email': 'avramneoko6@gmail.com',
        'passport_number': 'HB2072131',
        'bank_account': {
            'currency': 'BYN'
        }
    }

    def test_new_customer(self, client, customer_repository, bank_account_repository):
        response = client.post('/api/customers/', json=self.CUSTOMER_DATA)

        assert response.status_code == HTTPStatus.CREATED
        assert 'uuid' in response.json
        assert customer_repository.check_customer(response.json['uuid'])
        assert customer_repository.has_bank_account(response.json['uuid'])

    def test_duplicated_new_customer(self, client):
        client.post('/api/customers/', json=self.CUSTOMER_DATA)
        response = client.post('/api/customers/', json=self.CUSTOMER_DATA)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'error' in response.json
        assert response.json['error'] == 'Customer already exists!'

    def test_wrong_passport_number_format(self, client):
        wrong_data = self.CUSTOMER_DATA.copy()
        wrong_data['passport_number'] = '123'

        response = client.post('/api/customers/', json=wrong_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_wrong_email_format(self, client):
        wrong_data = self.CUSTOMER_DATA.copy()
        wrong_data['email'] = 'some@@'

        response = client.post('/api/customers/', json=wrong_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestCustomerUpdate:
    CUSTOMER_DATA = {
        'first_name': 'Ilya',
        'last_name': 'Auramenka',
        'email': 'avramneoko6@gmail.com',
        'passport_number': 'HB2072131',
        'bank_account': {
            'currency': 'BYN'
        }
    }

    def test_one_field_customer_update(self, client, customer_repository):
        new_customer = client.post('/api/customers/', json=self.CUSTOMER_DATA)
        update_data = {
            'first_name': 'George',
        }

        response = client.patch(
            f'/api/customers/{new_customer.json["uuid"]}',
            json=update_data
        )

        updated_customer = customer_repository.get_customer(
            new_customer.json['uuid']
        )

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert updated_customer.first_name == update_data['first_name']

    def test_full_customer_update(self, client, customer_repository):
        new_customer = client.post('/api/customers/', json=self.CUSTOMER_DATA)
        update_data = {
            'first_name': 'George',
            'last_name': 'Kitov',
            'email': 'something@mail.com',
        }

        response = client.patch(
            f'/api/customers/{new_customer.json["uuid"]}',
            json=update_data
        )

        updated_customer = customer_repository.get_customer(
            new_customer.json['uuid']
        )

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert updated_customer.first_name == update_data['first_name']
        assert updated_customer.last_name == update_data['last_name']
        assert updated_customer.email == update_data['email']

    def test_wrong_email_format(self, client):
        update_data = {
            'email': 'something@@@mail.com',
        }

        new_customer = client.post('/api/customers/', json=self.CUSTOMER_DATA)

        response = client.patch(
            f'/api/customers/{new_customer.json["uuid"]}',
            json=update_data
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
