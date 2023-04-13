from flask import Blueprint
from flask.cli import with_appcontext

cli_manage = Blueprint('manage', __name__, cli_group=None)


@cli_manage.cli.command("init-db")
@with_appcontext
def init_db():
    from src.application import seed_database, initialize_database_proxy

    from psycopg2.errors import DuplicateDatabase

    from src.application.configuration import AbstractConfig

    from flask import current_app

    configuration = AbstractConfig(current_app.config)

    try:
        from psycopg2 import connect

        connection = connect(
            host=configuration.APPLICATION_DATABASE_HOST,
            port=configuration.APPLICATION_DATABASE_PORT,
            user=configuration.APPLICATION_DATABASE_USER,
            password=configuration.APPLICATION_DATABASE_PASSWORD)

        connection.autocommit = True

        cursor = connection.cursor()

        current_app.logger.info(f"Creating database '{configuration.APPLICATION_DATABASE_NAME}'")

        cursor.execute(f"CREATE DATABASE {configuration.APPLICATION_DATABASE_NAME}")

        connection.close()

        cursor.close()

    except DuplicateDatabase:
        pass

    initialize_database_proxy(
        database=configuration.APPLICATION_DATABASE_NAME,
        host=configuration.APPLICATION_DATABASE_HOST,
        port=configuration.APPLICATION_DATABASE_PORT,
        user=configuration.APPLICATION_DATABASE_USER,
        password=configuration.APPLICATION_DATABASE_PASSWORD)

    current_app.logger.info("Creating database tables")

    seed_database(configuration.APPLICATION_PRODUCT_SERVICE)
