from http import HTTPStatus
from injector import inject
from app.repositories.sqlalchemy.customer import CustomerRepository
from flask_restful import Resource
from app.schemas.customer import CustomerCreateSchema, CustomerUpdateSchema, CustomerRetrieveSchema
from webargs.flaskparser import use_args
from app.utils.response_serializer import serialize_response


class CustomersResource(Resource):
    @inject
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    @use_args(CustomerCreateSchema())
    @serialize_response(CustomerCreateSchema(), HTTPStatus.CREATED)
    def post(self, customer):
        return self.repository.create_customer(customer)


class CustomerResource(Resource):
    @inject
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    @use_args(CustomerUpdateSchema())
    @serialize_response(None, HTTPStatus.NO_CONTENT)
    def patch(self, customer, uuid: str):
        self.repository.update_customer(uuid, customer)

    @serialize_response(None, HTTPStatus.NO_CONTENT)
    def delete(self, uuid: str):
        self.repository.delete_customer(uuid)

    @serialize_response(CustomerRetrieveSchema(), HTTPStatus.OK)
    def get(self, uuid: str):
        return self.repository.get_customer(uuid)
