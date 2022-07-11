from app.app import create_app
from flask import current_app, jsonify
from flask_sqlalchemy import get_debug_queries
from app.exceptions import AppException, app_exception_handler


app = create_app()


@app.after_request
def after_request(response):
    current_app.logger.info('------------------')
    queries = get_debug_queries()
    current_app.logger.info(f'QUERIES COUNT: {len(queries)}')
    for query in queries:
        current_app.logger.info(
            '%s\n'
            '***Parameters: %s\n'
            '***Duration: %fs\n'
            '***Context: %s\n'
            % (query.statement, query.parameters, query.duration,
               query.context))
    current_app.logger.info('------------------')
    return response


@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code


app.errorhandler(AppException)(app_exception_handler)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
