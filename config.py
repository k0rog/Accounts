import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    IBAN_COUNTRY_IDENTIFIER = os.environ.get('IBAN_COUNTRY_IDENTIFIER')
    IBAN_BBAN_LENGTH = os.environ.get('IBAN_BBAN_LENGTH')
    IBAN_BANK_IDENTIFIER = os.environ.get('IBAN_BANK_IDENTIFIER')
