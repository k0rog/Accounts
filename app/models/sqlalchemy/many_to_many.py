from app.storage.sqlalchemy import db


bank_accounts = db.Table(
    'bank_accounts',
    db.Column('customer_id', db.String(9), db.ForeignKey('customer.passport_number'), primary_key=True),
    db.Column('bank_account_id', db.String(34), db.ForeignKey('bank_account.IBAN'), primary_key=True)
)
