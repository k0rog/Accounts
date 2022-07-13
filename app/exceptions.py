from http import HTTPStatus
from flask import make_response


class AppException(Exception):
    """Base exception to be caught"""


class AlreadyExistsException(AppException):
    """Duplicate PK"""


class ValidationException(AppException):
    """Domain constraint violation"""


def app_exception_handler(exception):
    http_code = 418
    if isinstance(exception, AlreadyExistsException):
        http_code = HTTPStatus.BAD_REQUEST
    elif isinstance(exception, ValidationException):
        http_code = HTTPStatus.BAD_REQUEST
    r = make_response(
        {'error': str(exception)}, http_code
    )
    return r
