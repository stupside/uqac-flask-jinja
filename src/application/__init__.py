from urllib import request
from json import loads

from src.domain import database_proxy

from src.domain.models import CreditCard, Order, Product, ShippingInformation, Transaction, OrderLine


def seed_database(products_uri: str):
    if Product.table_exists():
        result = request.urlopen(products_uri)

        buffer = result.read()

        json = loads(bytes(buffer))

        for product in json["products"]:
            try:
                Product.insert(product).on_conflict_ignore().execute()
            except ValueError:
                # Null bytes will throw, but I don't care. Don't send me null bytes in json strings.
                pass


def initialize_database_proxy(database: str, host: str, port: int, user: str, password: str):
    from playhouse.pool import PooledPostgresqlExtDatabase

    pooled_connection = PooledPostgresqlExtDatabase(database=database, host=host, port=port, user=user,
                                                    password=password)

    database_proxy.initialize(pooled_connection)

    tables = [CreditCard, Order, Product, OrderLine, ShippingInformation, Transaction]

    database_proxy.create_tables(tables)

    pooled_connection.close()
