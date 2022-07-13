def test_new_customer(client):
    request_data = {
        'first_name': 'Ilya',
        'last_name': 'Auramenka',
        'email': 'avramneoko6@gmail.com',
        'passport_number': 'HB2072131',
        'bank_account': {
            'currency': 'BYN'
        }
    }
    response = client.post('/api/customers/', json=request_data)

    print(response)
    print(response.__dict__)
    print(response.json)
