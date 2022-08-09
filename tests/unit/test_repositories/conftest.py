import pytest

from sqlalchemy.exc import IntegrityError

from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.many_to_many import AssociationBankAccountCustomer


@pytest.fixture(scope='session')
def permanent_session(db):
    session = db.session
    yield session
    session.close()
    
    
@pytest.fixture(scope='session')
def bank_account(permanent_session):
    while True:
        try:
            bank_account = BankAccount(
                currency='BYN',
                balance=0,
            )

            permanent_session.add(bank_account)
            permanent_session.commit()

            break
        except IntegrityError:
            '''There's very small chance to generate duplicated IBAN
            But since this chance still exists, we have to repeat the operation'''
            permanent_session.rollback()

    association_row = AssociationBankAccountCustomer(
        bank_account_id=bank_account.IBAN,
        customer_id='MockUUID'
    )

    permanent_session.add(association_row)
    permanent_session.commit()

    yield bank_account
