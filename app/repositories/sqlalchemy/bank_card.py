from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from app.exceptions import DoesNotExistException
from app.models.sqlalchemy.bank_card import BankCard


class BankCardRepository:
    @inject
    def __init__(
            self,
            storage: SQLAlchemy,
    ):
        self._storage = storage

    def create(self, data: dict, bank_account_iban: str) -> tuple[BankCard, str, str]:
        while True:
            try:
                bank_card = BankCard(
                    expiration_date=data['expiration_date'],
                    bank_account_iban=bank_account_iban,
                )

                self._storage.session.add(bank_card)
                self._storage.session.commit()

                break
            except IntegrityError as e:
                self._storage.session.rollback()

                if isinstance(e.orig, ForeignKeyViolation):
                    raise DoesNotExistException('BankAccount does not exist!')

                if isinstance(e.orig, UniqueViolation):
                    '''There's very small chance to generate duplicated card_number
                    But since this chance still exists, we have to repeat the operation'''
                    continue

                raise e

        cvv = BankCard.generate_cvv()
        pin = BankCard.generate_pin()

        bank_card.set_cvv(cvv)
        bank_card.set_pin(pin)

        self._storage.session.commit()

        return bank_card, pin, cvv

    def get_by_card_number(self, card_number: str) -> BankCard:
        bank_card = self._storage.session.query(
            BankCard
        ).filter_by(card_number=card_number).first()

        if not bank_card:
            raise DoesNotExistException('BankCard does not exist!')

        return bank_card

    def get_attached_to_bank_account(self, bank_account_iban: str) -> list[BankCard]:
        return self._storage.session.query(
            BankCard
        ).filter_by(bank_account_iban=bank_account_iban).all()

    def bulk_delete(self, card_numbers: list[str]) -> bool:
        is_deleted = self._storage.session.query(
            BankCard
        ).filter(BankCard.card_number.in_(card_numbers)).delete()

        self._storage.session.commit()

        return is_deleted

    def delete(self, card_number: str) -> bool:
        is_deleted = self._storage.session.query(
            BankCard
        ).filter_by(card_number=card_number).delete()

        self._storage.session.commit()

        return is_deleted
