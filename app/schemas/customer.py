from marshmallow import fields, Schema, validates, ValidationError, validate
import re
from app.schemas.bank_account import BankAccountSchema


class CustomerCreateSchema(Schema):
    passport_number = fields.String(required=True, load_only=True)
    first_name = fields.String(required=True, validate=validate.Length(max=64))
    last_name = fields.String(required=True, validate=validate.Length(max=64))
    email = fields.String(required=True)
    bank_account = fields.Nested(BankAccountSchema, required=True)

    @validates('passport_number')
    def validate_passport_number(self, passport_number):
        if re.match(r'[a-zA-Z]{2}\d{7}', passport_number) is None:
            raise ValidationError("Not valid passport number")
        return passport_number[:2].upper() + passport_number[2:]

    @validates('email')
    def validate_email(self, email):
        if re.match(r'[^@]+@[^@]+\.[^@]+', email) is None:
            raise ValidationError("Not valid email address")
        return email


class CustomerUpdateSchema(Schema):
    first_name = fields.String(validate=validate.Length(max=64))
    last_name = fields.String(validate=validate.Length(max=64))
    email = fields.String()

    @validates('email')
    def validate_email(self, email):
        if re.match(r'[^@]+@[^@]+\.[^@]+', email) is None:
            raise ValidationError("Not valid email address")
        return email


