from app.app import create_app
from flask import current_app, jsonify
from flask_sqlalchemy import get_debug_queries
from app.exceptions import AppException, app_exception_handler


app = create_app()


@app.after_request
def after_request(response):
    """Logs database request content and database request count per every client request"""
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


from app.storage.sqlalchemy import db
from app.models.sqlalchemy.bank_account import BankAccount


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'BankAccount': BankAccount}


if __name__ == '__main__':
    app.run(host='0.0.0.0', load_dotenv=True)
