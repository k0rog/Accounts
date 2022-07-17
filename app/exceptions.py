from http import HTTPStatus
from flask import make_response, jsonify


class AppException(Exception):
    """Base exception to be caught"""


class AlreadyExistException(AppException):
    """Duplicate PK"""


class ValidationException(AppException):
    """Domain constraint violation"""


class DoesNotExistException(AppException):
    """Domain constraint violation"""


def app_exception_handler(exception):
    http_code = 418
    if isinstance(exception, AlreadyExistException):
        http_code = HTTPStatus.BAD_REQUEST
    elif isinstance(exception, ValidationException):
        http_code = HTTPStatus.BAD_REQUEST
    elif isinstance(exception, DoesNotExistException):
        http_code = HTTPStatus.BAD_REQUEST
    r = make_response(
        {'error': str(exception)}, http_code
    )
    return r


def api_exception_handler(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
