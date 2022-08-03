import pytest

from app.app import create_app
from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.repositories.sqlalchemy.customer import CustomerRepository
from app.repositories.sqlalchemy.bank_card import BankCardRepository
from app.storage.sqlalchemy import db


@pytest.fixture(scope='session')
def app():
    app = create_app(dotenv_filename='.env.test')
    app.config.update({
        'TESTING': True,
    })

    yield app


@pytest.fixture(scope='function')
def storage(app):
    context = app.test_request_context()
    context.push()

    db.create_all()

    yield db

    db.drop_all()
    context.pop()


@pytest.fixture(scope='function')
def client(app, storage):
    client = app.test_client()

    yield client


@pytest.fixture(scope='function')
def bank_account_repository(app, storage):
    repository = BankAccountRepository(
        storage=storage,
        config=app.config
    )

    yield repository


@pytest.fixture(scope='function')
def customer_repository(bank_account_repository, storage):
    repository = CustomerRepository(
        storage=storage,
        bank_account_repository=bank_account_repository
    )

    yield repository


@pytest.fixture(scope='function')
def bank_card_repository(storage):
    repository = BankCardRepository(
        storage=storage,
    )

    yield repository
