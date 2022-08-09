import pytest

from app.services.customer import CustomerService
from app.services.bank_account import BankAccountService
from app.services.bank_card import BankCardService


@pytest.fixture(scope='function')
def customer_service(storage, bank_account_repository, customer_repository):
    customer_service = CustomerService(
        customer_repository=customer_repository,
        bank_account_repository=bank_account_repository
    )

    yield customer_service


@pytest.fixture(scope='function')
def bank_account_service(storage, bank_account_repository) -> BankAccountService:
    bank_account_service = BankAccountService(
        bank_account_repository=bank_account_repository
    )

    yield bank_account_service


@pytest.fixture(scope='function')
def bank_card_service(storage, bank_card_repository):
    bank_card_service = BankCardService(
        bank_card_repository=bank_card_repository
    )

    yield bank_card_service
