from typing import Any

from dacite import from_dict

from flask import Blueprint, json, request, redirect, url_for, jsonify, current_app

from src.application.configuration import AbstractConfig

from src.application.exceptions import ApplicationError, Error
from src.application.features import Mediator

from src.application.features.orders.create_order import CreateOrder
from src.application.features.orders.pay_order import PayOrder
from src.application.features.orders.update_order_infos import UpdateOrder
from src.application.requests.orders.get_order import GetOrder

orders_blueprint = Blueprint('orders', __name__, url_prefix="order")


@orders_blueprint.route("/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    redis_connection = AbstractConfig(current_app.config).REDIS_CONNECTION

    cache = redis_connection.get(order_id)

    order: Any | None = None

    if cache:
        order = json.loads(cache)

    if not order:
        order = GetOrder.handle(order_id)

        redis_connection.set(order_id, json.dumps(order))

    paid = order["paid"]

    if order:
        if paid or (order["transaction"] and order["transaction"]["error"]):
            code = 200
        else:
            code = 202

        return jsonify(order), code


@orders_blueprint.route("/", methods=["POST"])
def create_order():
    data = json.loads(request.data)

    if "product" in data:
        command = from_dict(data_class=CreateOrder.V1, data=data)
    elif "products" in data:
        command = from_dict(data_class=CreateOrder.V2, data=data)
    else:
        raise ApplicationError(400, {"order": [
            Error("bad-request", "product missing")
        ]})

    order_id = Mediator.dispatch(command)

    return redirect(url_for("api.orders.get_order", order_id=order_id))


@orders_blueprint.route("/<int:order_id>", methods=["PUT"])
def update_order_infos(order_id: int):
    data = json.loads(request.data)

    if "order" in data and "credit" in data:
        raise ApplicationError(400, {"order": [
            Error("bad-request", "either order or credit accepted")
        ]})

    if "order" in data:
        command = UpdateOrder()

        command.order_id = order_id

        command.order = from_dict(data_class=UpdateOrder.Order, data=data["order"])

        Mediator.dispatch(command)

    elif "credit_card" in data:
        command = PayOrder()

        command.order_id = order_id

        command.credit_card = from_dict(data_class=PayOrder.CreditCard, data=data["credit_card"])

        Mediator.dispatch(command)

        return '', 202

    else:
        raise ApplicationError(400, {"order": [
            Error("bad-request", "order or credit card missing")
        ]})

    return redirect(url_for("api.orders.get_order", order_id=order_id))
