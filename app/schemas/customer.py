from marshmallow import fields, Schema, validates, ValidationError, validate
import re
from app.schemas.bank_account import BankAccountSchema


class BaseCustomerSchema(Schema):
    passport_number = fields.String(required=True)
    first_name = fields.String(required=True, validate=validate.Length(max=64))
    last_name = fields.String(required=True, validate=validate.Length(max=64))
    email = fields.String(required=True)

    @validates('passport_number')
    def validate_passport_number(self, passport_number):
        if re.match(r'^[a-zA-Z]{2}\d{7}$', passport_number) is None:
            raise ValidationError("Not a valid passport_number format.")
        return passport_number[:2].upper() + passport_number[2:]

    @validates('email')
    def validate_email(self, email):
        if re.match(r'[^@]+@[^@]+\.[^@]+', email) is None:
            raise ValidationError("Not a valid email format.")
        return email


class CustomerCreateSchema(BaseCustomerSchema):
    class Meta:
        load_only = ('first_name', 'last_name', 'email', 'passport_number', 'bank_account')

    uuid = fields.String()
    bank_account = fields.Nested(BankAccountSchema, required=True)


class CustomerUpdateSchema(BaseCustomerSchema):
    passport_number = fields.String()
    first_name = fields.String(validate=validate.Length(max=64))
    last_name = fields.String(validate=validate.Length(max=64))
    email = fields.String()


class CustomerRetrieveSchema(BaseCustomerSchema):
    pass
