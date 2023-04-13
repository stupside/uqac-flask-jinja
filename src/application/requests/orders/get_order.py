from peewee import DoesNotExist, JOIN
from playhouse.shortcuts import model_to_dict

from src.application.exceptions import Error, ApplicationError
from src.domain.models import Order, CreditCard, ShippingInformation, Transaction


class GetOrder:

    @staticmethod
    def handle(order_id: int):

        credit_card_query = (CreditCard.select(
            CreditCard.name,
            CreditCard.first_digits,
            CreditCard.last_digits,
            CreditCard.expiration_year,
            CreditCard.expiration_month))

        shipping_information_query = (ShippingInformation.select(
            ShippingInformation.country,
            ShippingInformation.address,
            ShippingInformation.postal_code,
            ShippingInformation.city,
            ShippingInformation.province))

        transaction_query = (Transaction.select(
            Transaction.error,
            Transaction.amount_charged,
            Transaction.success))

        try:
            order = (
                Order.select(
                    Order,
                    *credit_card_query.selected_columns,
                    *shipping_information_query.selected_columns,
                    *transaction_query.selected_columns
                )
                .join_from(Order, CreditCard, JOIN.LEFT_OUTER)
                .join_from(Order, ShippingInformation, JOIN.LEFT_OUTER)
                .join_from(Order, Transaction, JOIN.LEFT_OUTER)
                .where(Order.id == order_id).get())

        except DoesNotExist:
            raise ApplicationError(404, {Order.__name__: [Error("not-found", "order not found")]})

        is_paid = ((round(order.transaction.amount_charged, 1) >= (round(order.total_price + order.shipping_price, 1)))
                   if order.transaction else False)

        return {
            "id": order.id,

            "email": order.email,

            "total_price": order.total_price,
            "shipping_price": order.shipping_price,

            "credit_card": (model_to_dict(order.credit_card, fields_from_query=credit_card_query)
                            if order.credit_card else None),

            "shipping_information": (
                model_to_dict(order.shipping_information, fields_from_query=shipping_information_query)
                if order.shipping_information else None),

            "products": list(order.order_lines.dicts()),

            "paid": is_paid,
            "transaction": (model_to_dict(order.transaction, fields_from_query=transaction_query)
                            if order.transaction else None),
        }
