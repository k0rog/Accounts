from abc import ABC, abstractmethod


class BaseCustomerRepository(ABC):

    @abstractmethod
    def check_customer(self, passport_number: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_customer(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    def update_customer(self, passport_number: str, data: dict):
        raise NotImplementedError

    @abstractmethod
    def has_bank_account(self, passport_number: str) -> bool:
        raise NotImplementedError


class BaseBankAccountRepository(ABC):
    @abstractmethod
    def create_bank_account(self, currency: str, balance: float = 0.0):
        raise NotImplementedError

    @abstractmethod
    def _get_unique_iban(self):
        raise NotImplementedError
