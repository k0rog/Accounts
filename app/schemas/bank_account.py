from marshmallow import fields, Schema, validates, ValidationError, validate
import re


ALLOWED_CURRENCY_LIST = ['BYN', 'EUR', 'USD']


class BankAccountSchema(Schema):
    class Meta:
        load_only = ('currency',)

    IBAN = fields.String()
    currency = fields.String(required=True)
    balance = fields.Float()

    @validates('IBAN')
    def validate_iban(self, iban):
        if re.match(r'[a-zA-Z]{2}[0-9a-zA-Z]{6}\d{20}', iban) is None:
            raise ValidationError("Wrong iban format")
        return iban

    @validates('currency')
    def validate_currency(self, currency):
        if currency.upper() not in ALLOWED_CURRENCY_LIST:
            raise ValidationError("Not allowed currency")
        return currency
