from http import HTTPStatus
from flask import make_response, jsonify


class AppException(Exception):
    pass


class AlreadyExists(AppException):
    pass


class ValidationError(AppException):
    pass


def app_exception_handler(exception):
    http_code = 418
    if isinstance(exception, AlreadyExists):
        http_code = HTTPStatus.BAD_REQUEST
    elif isinstance(exception, ValidationError):
        http_code = HTTPStatus.BAD_REQUEST
    r = make_response(
        {'error': str(exception)}, http_code
    )
    return r
