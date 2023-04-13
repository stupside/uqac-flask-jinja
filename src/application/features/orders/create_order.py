from dataclasses import dataclass

from peewee import DoesNotExist

from src.application.exceptions import ApplicationError, Error
from src.application.features import Mediator
from src.domain import database_proxy
from src.domain.models import Product, Order, OrderLine


@dataclass
class CreateOrderProduct:
    id: int
    quantity: int


class CreateOrder:
    @dataclass
    class V1:
        product: CreateOrderProduct

    @dataclass
    class V2:
        products: list[CreateOrderProduct]


@Mediator.validate.register(CreateOrder.V1)
def validate(command: CreateOrder.V1):
    if not command.product.id or command.product.id < 1:
        return Product.__name__, [
            Error("invalid-fields", "Invalid product id")
        ], 422

    if not command.product.quantity or command.product.quantity < 1:
        return Product.__name__, [
            Error("invalid-fields", "Invalid quantity")
        ], 422


@Mediator.validate.register(CreateOrder.V2)
def validate(command: CreateOrder.V2):
    if len(command.products) == 0:
        return Product.__name__, [
            Error("bad-request", "At least one product can be ordered")
        ], 403

    for product in command.products:
        if not product.id or product.id < 1:
            return Product.__name__, [
                Error("invalid-fields", "Invalid product id")
            ], 422

        if not product.quantity or product.quantity < 1:
            return Product.__name__, [
                Error("invalid-fields", "Invalid quantity")
            ], 422


@Mediator.handle.register(CreateOrder.V1)
def handle(command: CreateOrder.V1):

    with database_proxy.atomic():

        order = Order()

        order.save()

        try:
            product = Product.select(Product.id, Product.weight, Product.price, Product.in_stock).where(
                Product.id == command.product.id).get()

        except DoesNotExist:
            raise ApplicationError(404, {Product.__name__: [Error("not-found", "product not found")]})

        if not product.in_stock:
            raise ApplicationError(422,
                                   {Product.__name__: [Error("out-of-stock", "product is out of stock")]})

        order_line = OrderLine()

        order_line.product = product.id
        order_line.quantity = command.product.quantity
        order_line.price_unit = product.price

        order_line.order = order

        order_line.save()

    return order.id


@Mediator.handle.register(CreateOrder.V2)
def handle(command: CreateOrder.V2):

    with database_proxy.atomic():

        order = Order()

        order.save()

        for add in command.products:

            try:
                product = Product.select(Product.id, Product.weight, Product.price, Product.in_stock).where(
                    Product.id == add.id).get()

            except DoesNotExist:
                raise ApplicationError(404, {Product.__name__: [Error("not-found", "product not found")]})

            if not product.in_stock:
                raise ApplicationError(422,
                                       {Product.__name__: [Error("out-of-stock", "product is out of stock")]})

            order_line = OrderLine()

            order_line.product = product.id
            order_line.quantity = add.quantity
            order_line.price_unit = product.price

            order_line.order = order

            order_line.save()

    return order.id
