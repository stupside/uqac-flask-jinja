import dataclasses
import json
from dataclasses import dataclass
from json import loads
from urllib import request
from urllib.error import HTTPError

from dacite import from_dict
from flask import current_app
from redis.client import Redis

from src.application.configuration import AbstractConfig
from src.domain import database_proxy
from src.domain.models import Transaction, CreditCard, Order


def payment_job(endpoint: str, order_id: int, credit_card: str, amount_charged: float):
    try:
        req = request.Request(endpoint)

        req.add_header("Content-Type", "application/json; charset=utf-8")

        body = json.dumps({
            "credit_card": json.loads(credit_card),
            "amount_charged": amount_charged
        })

        with request.urlopen(endpoint, body.encode("utf-8")) as result:

            response = from_dict(data_class=Pay.Response, data=loads(result.read()))

            with database_proxy.atomic():
                credit_card = CreditCard.insert(response.credit_card.__dict__).execute()

                transaction = Transaction.insert({
                    Transaction.external_id: response.transaction.id,
                    Transaction.amount_charged: response.transaction.amount_charged,
                    Transaction.success: True
                }).execute()

                Order.update({Order.credit_card: credit_card, Order.transaction: transaction}).where(
                    Order.id == order_id).execute()

    except HTTPError as error:

        if error.code == 422:
            error = json.dumps(loads(error.read())["errors"]["credit_card"])

        elif error.code == 401:
            error = json.dumps({"code": "card-declined", "name": "invalid credit card"})

        else:
            error = json.dumps({"code": "payment-service", "name": "card declined"})

        with database_proxy.atomic():

            transaction = Transaction.insert({
                Transaction.error: error,
                Transaction.success: False
            }).execute()

            Order.update({Order.transaction: transaction.id}).where(
                Order.id == order_id).execute()

    finally:

        redis_connection = AbstractConfig(current_app.config).REDIS_CONNECTION

        redis_connection.delete(order_id)

    return response


class Pay:
    @dataclass
    class CreditCard:
        name: str
        number: str
        cvv: str
        expiration_month: int
        expiration_year: int

    @dataclass
    class Response:
        @dataclass
        class CreditCard:
            name: str
            first_digits: str
            last_digits: int
            expiration_year: int
            expiration_month: int

        @dataclass
        class Transaction:
            id: str
            success: str
            amount_charged: float

        credit_card: CreditCard
        transaction: Transaction

    @staticmethod
    def has_payment_processing(redis: Redis, order_id: int):
        from rq import Queue

        queue = Queue("payments", connection=redis)

        job = queue.fetch_job(str(order_id))

        if job:
            status = job.get_status()

            from rq.job import JobStatus

            return status != JobStatus.CANCELED or status != JobStatus.FAILED

        return False

    @staticmethod
    def enqueue_payment(redis: Redis, endpoint: str, order_id: int, credit_card: CreditCard, amount_charged: float):
        from rq import Queue
        from rq.job import Job

        job = Job.create(
            payment_job,
            args=(endpoint, order_id, json.dumps(dataclasses.asdict(credit_card)), amount_charged),
            connection=redis,
            id=str(order_id)
        )

        queue = Queue("payments", connection=redis)

        queue.enqueue_job(job)
