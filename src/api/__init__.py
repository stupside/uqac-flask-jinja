from dacite import WrongTypeError, MissingValueError
from flask import Blueprint, jsonify

from src.api.views import api_blueprint
from src.application.exceptions import ApplicationError, Error

from src.api.views.orders import orders_blueprint
from src.api.views.products import products_blueprint

from src.domain import database_proxy


@api_blueprint.errorhandler(ApplicationError)
def application_error(error: ApplicationError):
    return jsonify(error.to_dict()), error.code


@api_blueprint.errorhandler(WrongTypeError)
def wrong_type_error(error: WrongTypeError):
    return application_error(ApplicationError(400, {
        error.field_path: [
            Error("invalid-field", str(error))
        ]
    }))


@api_blueprint.errorhandler(ValueError)
def missing_value_error(error: ValueError):
    return application_error(ApplicationError(403, {
        "unknown": [
            Error("bad-request", "value error")
        ]
    }))


@api_blueprint.errorhandler(MissingValueError)
def missing_value_error(error: MissingValueError):
    return application_error(ApplicationError(400, {
        error.field_path: [
            Error("missing-field", str(error))
        ]
    }))


@api_blueprint.before_request
def _db_connect():
    if database_proxy.is_closed():
        database_proxy.connect()


@api_blueprint.teardown_request
def _db_close(_):
    if not database_proxy.is_closed():
        database_proxy.close()


api_blueprint.register_blueprint(products_blueprint)
api_blueprint.register_blueprint(orders_blueprint)
