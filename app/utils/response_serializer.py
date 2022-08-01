def serialize_response(schema, code):
    def outer(f):
        def inner(*args, **kwargs):
            result = f(*args, **kwargs)
            if schema is not None:
                serialized_response = schema.dump(result)
                return serialized_response, code
            return '', code
        return inner
    return outer
