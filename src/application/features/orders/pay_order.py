from dataclasses import dataclass
from datetime import date

from flask import current_app
from peewee import DoesNotExist, JOIN

from src.application.configuration import AbstractConfig
from src.application.exceptions import ApplicationError, Error
from src.application.features import Mediator, is_valid_string
from src.application.tasks.payment_task import Pay
from src.domain.models import Order, CreditCard, ShippingInformation, Transaction


class PayOrder:

    @dataclass
    class CreditCard(Pay.CreditCard):
        pass

    order_id: int

    credit_card: CreditCard


@Mediator.validate.register(PayOrder)
def validate(command: PayOrder):
    today = date.today()

    is_valid_expiration_date = (
            command.credit_card.expiration_year >= today.year
            and command.credit_card.expiration_month >= today.month
    )

    if (
            is_valid_string(command.credit_card.name)
            and len(command.credit_card.cvv) == 3
            and is_valid_expiration_date
    ):
        return

    return CreditCard.__name__, [Error("card-declined", "invalid credit card")], 422


@Mediator.handle.register(PayOrder)
def handle(command: PayOrder):
    try:
        order = (Order.select(Order.id, ShippingInformation.id, Order.transaction)
                 .join_from(Order, ShippingInformation, JOIN.LEFT_OUTER)
                 .join_from(Order, Transaction, JOIN.LEFT_OUTER)
                 .where(Order.id == command.order_id).get())

    except DoesNotExist:
        raise ApplicationError(404, {Order.__name__: [Error("not-found", "order not found")]})

    if not order.shipping_information:
        raise ApplicationError(422, {
            Order.__name__: [Error("missing-fields", "client shipping information and email must be updated")]})

    if order.transaction and order.transaction.success:
        raise ApplicationError(409, {
            Order.__name__: [Error("payment-processed", "payment already processed")]})

    configuration = AbstractConfig(current_app.config)

    redis = configuration.REDIS_CONNECTION

    if Pay.has_payment_processing(redis, order.id):
        raise ApplicationError(409, {
            Order.__name__: [Error("payment-processing", "payment is being processed")]})

    Pay.enqueue_payment(redis, configuration.APPLICATION_SHOP_SERVICE, order.id,
                        command.credit_card,
                        order.total_price + order.shipping_price)

