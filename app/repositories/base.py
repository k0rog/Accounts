from abc import ABC, abstractmethod


class BaseCustomerRepository(ABC):

    @abstractmethod
    def check_customer(self, passport_number: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_customer(self, data: dict):
        raise NotImplementedError


class BaseBankAccountRepository(ABC):
    @abstractmethod
    def create_bank_account(self, currency: str, balance: float = 0.0):
        raise NotImplementedError

    @abstractmethod
    def get_unique_iban(self):
        raise NotImplementedError
