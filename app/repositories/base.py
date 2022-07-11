from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    def check_customer(self, passport_number: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_customer(self, data: dict):
        raise NotImplementedError
