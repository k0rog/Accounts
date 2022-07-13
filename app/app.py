from flask import Flask
from flask_restful import Api
from injector import Injector
from flask_injector import FlaskInjector
from app.dependency_injection import SQLAlchemyModule
from app.resources.customer import CustomerResource
from config import AppConfig, update_config_class


api = Api()


def create_app(config_class: object = AppConfig, dotenv_filename: str = ''):
    app = Flask(__name__)

    app.config.from_object(update_config_class(dotenv_filename, config_class))

    api.add_resource(CustomerResource, '/api/customers/', endpoint='customer')
    api.init_app(app)

    injector = Injector([SQLAlchemyModule(app=app, config=app.config)])
    FlaskInjector(app=app, injector=injector)

    return app


from app.models import sqlalchemy
