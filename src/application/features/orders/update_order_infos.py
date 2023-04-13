from dataclasses import dataclass

from peewee import DoesNotExist, JOIN

from src.application.configuration import AbstractConfig
from flask import current_app

from src.application.exceptions import ApplicationError, Error
from src.application.features import Mediator, is_valid_string
from src.domain import database_proxy
from src.domain.models import Order, ShippingInformation, Transaction


class UpdateOrder:
    @dataclass
    class Order:
        @dataclass
        class UpdateShippingInformation:
            country: str
            address: str
            postal_code: str
            city: str
            province: str

        email: str
        shipping_information: UpdateShippingInformation

    order_id: int
    order: Order


@Mediator.validate.register(UpdateOrder)
def validate(command: UpdateOrder):
    order = command.order
    shipping_information = order.shipping_information

    if (
            is_valid_string(order.email)
            and is_valid_string(shipping_information.country)
            and is_valid_string(shipping_information.address)
            and is_valid_string(shipping_information.postal_code)
            and is_valid_string(shipping_information.city)
            and is_valid_string(shipping_information.province)
    ):
        return

    return Order.__name__, [
        Error("missing-fields", "missing required field(s)")
    ], 422


@Mediator.handle.register(UpdateOrder)
def handle(command: UpdateOrder):
    try:
        order = (Order.select(Order.email, Order.shipping_information, Order.transaction)
                 .join_from(Order, ShippingInformation, JOIN.LEFT_OUTER)
                 .join_from(Order, Transaction, JOIN.LEFT_OUTER)
                 .where(Order.id == command.order_id).get())

    except DoesNotExist:
        raise ApplicationError(404, {Order.__name__: [Error("not-found", "order not found")]})

    if order.transaction and order.transaction.success:
        raise ApplicationError(409, {
            Order.__name__: [Error("payment-processed", "payment already processed")]})

    redis = AbstractConfig(current_app.config).REDIS_CONNECTION

    from src.application.tasks.payment_task import Pay

    if Pay.has_payment_processing(redis, order.id):
        raise ApplicationError(409, {
            Order.__name__: [Error("payment-processing", "payment is being processed")]})

    if order.shipping_information:
        shipping_information = order.shipping_information

        with database_proxy.atomic():

            shipping_information.update(command.order.shipping_information.__dict__).execute()

            order.update({
                Order.email: command.order.email
            }).where(Order.id == command.order_id).execute()

    else:

        with database_proxy.atomic():

            shipping_information = ShippingInformation.insert(command.order.shipping_information.__dict__).execute()

            order.update({
                Order.email: command.order.email,
                Order.shipping_information: shipping_information
            }).where(Order.id == command.order_id).execute()

    redis.delete(command.order_id)
