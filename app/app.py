from flask import Flask
from flask_restful import Api
from config import Config
from injector import Injector
from flask_injector import FlaskInjector
from app.dependency_injection import SQLAlchemyModule
from app.resources.customer import CustomerResource


api = Api()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    api.add_resource(CustomerResource, '/api/customers/', endpoint='customer')
    api.init_app(app)

    injector = Injector([SQLAlchemyModule(app=app)])
    FlaskInjector(app=app, injector=injector)

    return app


from app.models import sqlalchemy
