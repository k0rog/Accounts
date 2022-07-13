import os
from dotenv import load_dotenv


def update_config_class(dotenv_filename: str, config_class: object):
    """Sets config class fields according to .env file if the above is specified"""
    if not dotenv_filename:
        return config_class

    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, dotenv_filename))

    for key in dir(config_class):
        if key.isupper():
            setattr(config_class, key, os.environ.get(key, None))

    return config_class


class AppConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    SQLALCHEMY_RECORD_QUERIES = os.environ.get('SQLALCHEMY_RECORD_QUERIES')

    IBAN_COUNTRY_IDENTIFIER = os.environ.get('IBAN_COUNTRY_IDENTIFIER')
    IBAN_BBAN_LENGTH = os.environ.get('IBAN_BBAN_LENGTH')
    IBAN_BANK_IDENTIFIER = os.environ.get('IBAN_BANK_IDENTIFIER')
