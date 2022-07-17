from http import HTTPStatus
from injector import inject
from app.repositories.base import BaseCustomerRepository
from flask_restful import Resource
from app.schemas.customer import CustomerCreateSchema, CustomerUpdateSchema
from webargs.flaskparser import use_args
from app.utils.response_serializer import serialize_response


class CustomersResource(Resource):
    @inject
    def __init__(self, repository: BaseCustomerRepository):
        self.repository = repository

    @use_args(CustomerCreateSchema())
    @serialize_response(CustomerCreateSchema(), HTTPStatus.CREATED)
    def post(self, customer):
        return self.repository.create_customer(customer)


class CustomerResource(Resource):
    @inject
    def __init__(self, repository: BaseCustomerRepository):
        self.repository = repository

    @use_args(CustomerUpdateSchema())
    @serialize_response(None, HTTPStatus.NO_CONTENT)
    def patch(self, customer, uuid: str):
        self.repository.update_customer(uuid, customer)
