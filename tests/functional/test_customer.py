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

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert customer_repository.check_customer(self.CUSTOMER_DATA['passport_number'])
        assert customer_repository.has_bank_account(self.CUSTOMER_DATA['passport_number'])

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

    def test_customer_update(self, client, customer_repository):
        client.post('/api/customers/', json=self.CUSTOMER_DATA)
        update_data = {
            'first_name': 'George',
            'last_name': 'Kitov',
            'email': 'something@mail.com',
        }
        response = client.patch(
            f'/api/customers/{self.CUSTOMER_DATA["passport_number"]}',
            json=update_data
        )

        updated_customer = customer_repository.get_customer_by_passport_number(
            self.CUSTOMER_DATA['passport_number']
        )

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert updated_customer.first_name == update_data['first_name']
        assert updated_customer.last_name == update_data['last_name']
        assert updated_customer.email == update_data['email']

    def test_wrong_email_format(self, client):
        update_data = {
            'email': 'something@@@mail.com',
        }

        client.post('/api/customers/', json=self.CUSTOMER_DATA)

        response = client.patch(
            f'/api/customers/{self.CUSTOMER_DATA["passport_number"]}',
            json=update_data
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
