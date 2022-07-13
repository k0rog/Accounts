import pytest
from app.app import create_app
from app.storage.sqlalchemy import db


@pytest.fixture(scope='session')
def app():
    app = create_app(dotenv_filename='.env.test')
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture(scope='session')
def client(app):
    client = app.test_client()

    context = app.test_request_context()
    context.push()

    db.create_all()

    yield client

    db.drop_all()

    context.pop()
