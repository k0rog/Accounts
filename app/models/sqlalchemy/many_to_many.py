from app.storage.sqlalchemy import db


class AssociationBankAccountCustomer(db.Model):
    customer_id = db.Column(db.String(40), primary_key=True)
    bank_account_id = db.Column(db.String(34), db.ForeignKey('bank_account.IBAN', ondelete='CASCADE'), primary_key=True)
    bank_account = db.relationship('BankAccount', back_populates='customers')
