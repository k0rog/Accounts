from http import HTTPStatus
from flask_apispec import marshal_with, MethodResource, use_kwargs
from injector import inject
from app.repositories.base import BaseRepository
from flask_restful import Resource
from app.schemas.customer import CustomerCreateSchema
from webargs.flaskparser import use_args


class CustomerResource(MethodResource, Resource):
    @inject
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    @use_args(CustomerCreateSchema())
    @marshal_with(None, code=HTTPStatus.NO_CONTENT)
    def post(self, customer):
        self.repository.create_customer(customer)
        return ''
