from marshmallow import fields, Schema, validates, ValidationError, validate
import re
from app.schemas.bank_account import BankAccountSchema


class BaseCustomerSchema(Schema):
    passport_number = fields.String()
    first_name = fields.String(validate=validate.Length(max=64))
    last_name = fields.String(validate=validate.Length(max=64))
    email = fields.String()

    @validates('passport_number')
    def validate_passport_number(self, passport_number):
        if re.match(r'^[a-zA-Z]{2}\d{7}$', passport_number) is None:
            raise ValidationError("Not valid passport_number")
        return passport_number[:2].upper() + passport_number[2:]

    @validates('email')
    def validate_email(self, email):
        if re.match(r'[^@]+@[^@]+\.[^@]+', email) is None:
            raise ValidationError("Not valid email")
        return email


class CustomerCreateSchema(BaseCustomerSchema):
    class Meta:
        required = ('first_name', 'last_name', 'email', 'passport_number')
        load_only = ('first_name', 'last_name', 'email', 'passport_number', 'bank_account')

    uuid = fields.String()
    bank_account = fields.Nested(BankAccountSchema, required=True)


class CustomerUpdateSchema(BaseCustomerSchema):
    class Meta:
        required = ('first_name', 'last_name', 'email', 'passport_number')


class CustomerRetrieveSchema(BaseCustomerSchema):
    class Meta:
        strict = True
        required = ('passport_number', 'email', 'first_name', 'last_name')
