from http import HTTPStatus
from injector import inject
from app.services.customer import CustomerService
from flask_restful import Resource
from app.schemas.customer import CustomerCreateSchema, CustomerUpdateSchema, CustomerRetrieveSchema
from webargs.flaskparser import use_args
from app.utils.response_serializer import serialize_response


class CustomersResource(Resource):
    @inject
    def __init__(self, service: CustomerService):
        self.service = service

    @use_args(CustomerCreateSchema())
    @serialize_response(CustomerCreateSchema(), HTTPStatus.CREATED)
    def post(self, customer):
        return self.service.create(customer)


class CustomerResource(Resource):
    @inject
    def __init__(self, service: CustomerService):
        self.service = service

    @use_args(CustomerUpdateSchema())
    @serialize_response(None, HTTPStatus.NO_CONTENT)
    def patch(self, customer, uuid: str):
        self.service.update(uuid, customer)

    @serialize_response(None, HTTPStatus.NO_CONTENT)
    def delete(self, uuid: str):
        self.service.delete(uuid)

    @serialize_response(CustomerRetrieveSchema(), HTTPStatus.OK)
    def get(self, uuid: str):
        return self.service.get_by_uuid(uuid)
