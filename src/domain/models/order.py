from peewee import ForeignKeyField, IntegerField, CharField, fn, FloatField, Check, JOIN, AutoField
from playhouse.hybrid import hybrid_property

from . import Product
from .credit_card import CreditCard
from .shipping_information import ShippingInformation
from .transaction import Transaction

from .. import BaseModel


class Order(BaseModel):
    id = AutoField(primary_key=True)

    email = CharField(null=True)

    shipping_information = ForeignKeyField(ShippingInformation, null=True, unique=True)

    credit_card = ForeignKeyField(CreditCard, null=True, unique=True)

    transaction = ForeignKeyField(Transaction, null=True, unique=True)

    @hybrid_property
    def order_lines(self):
        # TODO: remove alias
        return OrderLine.select(OrderLine.product.alias("id"), OrderLine.quantity).where(OrderLine.order == self)

    @hybrid_property
    def total_price(self) -> float:
        return OrderLine.select(OrderLine.quantity, OrderLine.price_unit).select(
            fn.SUM(OrderLine.quantity * OrderLine.price_unit)).where(OrderLine.order == self).scalar()

    @hybrid_property
    def shipping_price(self) -> float:
        return OrderLine.select(fn.SUM(Product.shipping_price)).join_from(OrderLine, Product, JOIN.LEFT_OUTER).where(
            OrderLine.order == self).scalar()


class OrderLine(BaseModel):
    id = AutoField(primary_key=True)

    product = ForeignKeyField(Product)

    quantity = IntegerField(constraints=[Check("quantity > 0")])
    price_unit = FloatField(constraints=[Check("price_unit > 0")])

    order = ForeignKeyField(Order)
