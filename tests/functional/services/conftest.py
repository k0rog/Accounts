import pytest
from sqlalchemy.exc import IntegrityError

from app.services.customer import CustomerService
from app.services.bank_account import BankAccountService
from app.services.bank_card import BankCardService
from app.models.sqlalchemy.customer import Customer
from app.models.sqlalchemy.bank_account import BankAccount
from app.models.sqlalchemy.bank_card import BankCard


@pytest.fixture(scope='function')
def customer_service(storage, bank_account_repository, customer_repository):
    customer_service = CustomerService(
        customer_repository=customer_repository,
        bank_account_repository=bank_account_repository
    )

    yield customer_service


@pytest.fixture(scope='function')
def bank_account_service(storage, bank_account_repository):
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


@pytest.fixture(scope='function')
def customer(storage):
    customer = Customer(
        first_name='John',
        last_name='Smith',
        email='jsmith@gmail.com',
        passport_number='HB1111111',
    )

    storage.session.add(customer)
    storage.session.commit()

    yield customer


@pytest.fixture(scope='function')
def bank_account(storage):
    while True:
        try:
            iban = BankAccount.generate_iban(
                'BY',
                'JPCB',
                20
            )

            bank_account = BankAccount(
                IBAN=iban,
                currency='BYN',
            )

            storage.session.add(bank_account)
            storage.session.commit()

            break
        except IntegrityError:
            '''There's very small chance to generate duplicated IBAN
            But since this chance still exists, we have to repeat the operation'''

    yield bank_account


@pytest.fixture(scope='function')
def bank_card(storage):
    bank_card = BankCard(
        card_number='4422553366447755',
        expiration_date='2025-05-05',
        CVV='111',
    )

    storage.session.add(bank_card)
    storage.session.commit()

    yield bank_card
