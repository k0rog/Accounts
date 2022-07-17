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
        assert 'passport_number' not in response.json
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
        wrong_data['email'] = 'some@@'

        response = client.post('/api/customers/', json=wrong_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
