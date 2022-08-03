import pytest

from app.services.customer import CustomerService


@pytest.fixture(scope='function')
def customer_service(storage, bank_account_repository, customer_repository):
    customer_service = CustomerService(
        customer_repository=customer_repository,
        bank_account_repository=bank_account_repository
    )

    yield customer_service
