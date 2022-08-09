import pytest
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError

from app.app import create_app
from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.repositories.sqlalchemy.customer import CustomerRepository
from app.repositories.sqlalchemy.bank_card import BankCardRepository
from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.many_to_many import AssociationBankAccountCustomer
from app.models.sqlalchemy.customer import Customer
from app.storage.sqlalchemy import db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app(dotenv_filename='.env.test')
    app.config.update({
        'TESTING': True,
    })

    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def db(app):
    _db.create_all()
    yield _db
    # _db.close_all_sessions()
    _db.drop_all()


@pytest.fixture(scope='session')
def connection(db):
    connection = db.engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope='function')
def storage(connection) -> SQLAlchemy:
    trans = connection.begin()
    db.session = scoped_session(sessionmaker(bind=connection))
    nested = connection.begin_nested()

    @event.listens_for(db.session, "after_transaction_end")
    def end_savepoint(*args):
        nonlocal nested

        if not nested.is_active:
            nested = connection.begin_nested()

    yield db

    db.session.close()
    trans.rollback()


@pytest.fixture(scope='function')
def client(app, storage):
    client = app.test_client()

    yield client


@pytest.fixture(scope='function')
def bank_account_repository(app, storage) -> BankAccountRepository:
    repository = BankAccountRepository(
        storage=storage,
        config=app.config
    )

    yield repository


@pytest.fixture(scope='function')
def customer_repository(storage) -> CustomerRepository:
    repository = CustomerRepository(
        storage=storage,
    )

    yield repository


@pytest.fixture(scope='function')
def bank_card_repository(storage) -> BankCardRepository:
    repository = BankCardRepository(
        storage=storage,
    )

    yield repository


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


@pytest.fixture(scope='session')
def customer(permanent_session):
    customer = Customer(
        first_name='John',
        last_name='Smith',
        email='jsmith@gmail.com',
        passport_number='HB1111111',
    )

    permanent_session.add(customer)
    permanent_session.commit()

    yield customer
