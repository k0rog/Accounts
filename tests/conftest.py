import pytest
from app.app import create_app
from app.storage.sqlalchemy import db
from app.repositories.sqlalchemy.bank_account import BankAccountRepository
from app.repositories.sqlalchemy.customer import CustomerRepository


@pytest.fixture(scope='session')
def app():
    app = create_app(dotenv_filename='.env.test')
    app.config.update({
        "TESTING": True,
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
def bank_account_repository(app):
    repository = BankAccountRepository(
        storage=db,
        config=app.config
    )

    yield repository


@pytest.fixture(scope='function')
def customer_repository(bank_account_repository):
    repository = CustomerRepository(
        storage=db,
        bank_account_repository=bank_account_repository
    )

    yield repository
