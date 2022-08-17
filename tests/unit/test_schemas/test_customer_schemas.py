import uuid
import json

import marshmallow.exceptions
import pytest

from app.schemas.customer import CustomerRetrieveSchema, CustomerCreateSchema, CustomerUpdateSchema


CUSTOMER_FIRST_NAME = 'Ilya'
CUSTOMER_LAST_NAME = 'Auramenka'
CUSTOMER_EMAIL = 'avramneoko6@gmail.com'
CUSTOMER_PASSPORT_NUMBER = 'HB2072131'
BANK_ACCOUNT_CURRENCY = 'BYN'


CUSTOMER_DATA = {
    'first_name': 'Ilya',
    'last_name': 'Auramenka',
    'email': 'avramneoko6@gmail.com',
    'passport_number': 'HB2072131',
    'bank_account': {
        'currency': 'BYN'
    }
}


class TestCustomerCreateSchema:
    def test_with_valid_data(self):
        schema = CustomerCreateSchema()

        data = schema.loads(json.dumps(CUSTOMER_DATA))

        assert data['first_name'] == CUSTOMER_DATA['first_name']
        assert data['last_name'] == CUSTOMER_DATA['last_name']
        assert data['email'] == CUSTOMER_DATA['email']
        assert data['passport_number'] == CUSTOMER_DATA['passport_number']

        assert data['bank_account']['currency'] == CUSTOMER_DATA['bank_account']['currency']

    def test_dump(self):
        schema = CustomerCreateSchema()

        create_data = CUSTOMER_DATA.copy()
        create_data['uuid'] = str(uuid.uuid4())

        validated_dict = schema.loads(json.dumps(create_data))

        return_data = schema.dump(validated_dict)

        assert len(return_data) == 1
        assert 'uuid' in return_data

    def test_with_one_field_missing(self):
        wrong_data = CUSTOMER_DATA.copy()
        del wrong_data['first_name']
        schema = CustomerCreateSchema()

        with pytest.raises(marshmallow.exceptions.ValidationError) as exception_info:
            schema.loads(json.dumps(wrong_data))

        error_message_dict = exception_info.value.messages
        assert len(error_message_dict) == 1
        assert 'first_name' in error_message_dict
        assert error_message_dict['first_name'][0] == f'Missing data for required field.'

    def test_with_two_fields_missing(self):
        wrong_data = CUSTOMER_DATA.copy()
        del wrong_data['first_name']
        del wrong_data['last_name']
        schema = CustomerCreateSchema()

        with pytest.raises(marshmallow.exceptions.ValidationError) as exception_info:
            schema.loads(json.dumps(wrong_data))

        error_message_dict = exception_info.value.messages
        assert error_message_dict['first_name'][0] == f'Missing data for required field.'
        assert error_message_dict['last_name'][0] == f'Missing data for required field.'

    def test_with_nonexistent_currency(self):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data['bank_account']['currency'] = '123a'

        schema = CustomerCreateSchema()

        with pytest.raises(marshmallow.exceptions.ValidationError) as exception_info:
            schema.loads(json.dumps(wrong_data))

        error_message_dict = exception_info.value.messages
        assert len(error_message_dict) == 1
        assert 'bank_account' in error_message_dict
        assert error_message_dict['bank_account'][0] == f'Not a valid currency'

    @pytest.mark.parametrize('field,value', (('email', 'some@@@'), ('passport_number', '111')))
    def test_with_wrong_format(self, field, value):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data[field] = value

        schema = CustomerCreateSchema()

        with pytest.raises(marshmallow.exceptions.ValidationError) as exception_info:
            schema.loads(json.dumps(wrong_data))

        error_message_dict = exception_info.value.messages
        assert len(error_message_dict) == 1
        assert field in error_message_dict
        assert error_message_dict[field][0] == f'Not a valid {field} format.'

    def test_with_all_fields_having_wrong_format(self):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data.update({
            'email': 'some@@@',
            'passport_number': '111'
        })

        schema = CustomerCreateSchema()

        with pytest.raises(marshmallow.exceptions.ValidationError) as exception_info:
            schema.loads(json.dumps(wrong_data))

        error_message_dict = exception_info.value.messages
        assert error_message_dict['email'][0] == 'Not a valid email format.'
        assert error_message_dict['passport_number'][0] == 'Not a valid passport_number format.'

    @pytest.mark.parametrize('field', ('first_name', 'last_name', 'email', 'passport_number'))
    @pytest.mark.parametrize('value', (1,))
    def test_with_wrong_type(self, field, value):
        wrong_data = CUSTOMER_DATA.copy()
        wrong_data[field] = value

        schema = CustomerCreateSchema()

        with pytest.raises(marshmallow.exceptions.ValidationError) as exception_info:
            schema.loads(json.dumps(wrong_data))

        error_message_dict = exception_info.value.messages
        assert len(error_message_dict) == 1
        assert field in error_message_dict
        assert error_message_dict[field][0] == f'Not a valid string.'

    def test_with_all_fields_having_wrong_type(self):
        wrong_data = {
            'first_name': 1,
            'last_name': 1,
            'email': 1,
            'passport_number': 1,
            'bank_account': {
                'currency': 1
            }
        }

        schema = CustomerCreateSchema()

        with pytest.raises(marshmallow.exceptions.ValidationError) as exception_info:
            schema.loads(json.dumps(wrong_data))

        error_message_dict = exception_info.value.messages
        assert error_message_dict['first_name'][0] == f'Not a valid string.'
        assert error_message_dict['last_name'][0] == f'Not a valid string.'
        assert error_message_dict['email'][0] == f'Not a valid string.'
        assert error_message_dict['passport_number'][0] == f'Not a valid string.'

        assert error_message_dict['bank_account'][0] == f'Not a valid string.'


class TestCustomerUpdateSchema:
    def test_with_for_one_field(self):
        pass

    def test_with_for_all_fields(self):
        pass

    def test_with_wrong_format(self):
        raise NotImplementedError

    def test_with_all_fields_having_wrong_format(self):
        raise NotImplementedError

    def test_with_wrong_type(self):
        raise NotImplementedError

    def test_with_all_fields_having_wrong_type(self):
        raise NotImplementedError


class TestCustomerRetrieveSchema:
    def test_retrieve_schema(self):
        raise NotImplementedError
