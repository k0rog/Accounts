from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    def check_customer(self, passport_number: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_customer(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    def create_bank_account(self, currency: str, balance: float = 0.0):
        raise NotImplementedError

    @abstractmethod
    def get_unique_iban(self):
        raise NotImplementedError

    @abstractmethod
    def check_bank_account(self, iban: str) -> bool:
        raise NotImplementedError
