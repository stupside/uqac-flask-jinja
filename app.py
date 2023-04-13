import os

from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config.from_object(f"config.{os.environ.get('ENV').capitalize()}Config")

    from src.application.configuration import AbstractConfig

    configuration = AbstractConfig(app.config)

    from src.application import initialize_database_proxy
    from peewee import OperationalError

    try:
        app.logger.info("Setting up database proxy")

        initialize_database_proxy(
            database=configuration.APPLICATION_DATABASE_NAME,
            host=configuration.APPLICATION_DATABASE_HOST,
            port=configuration.APPLICATION_DATABASE_PORT,
            user=configuration.APPLICATION_DATABASE_USER,
            password=configuration.APPLICATION_DATABASE_PASSWORD)

    except OperationalError:
        app.logger.critical(
            "Database proxy failed to initialize. "
            "Make sure to init the database before running the app."
        )

    with app.app_context():
        from src.api import api_blueprint

        app.register_blueprint(api_blueprint)

        from src.cli import app_cli

        app.register_blueprint(app_cli, cli_group=None)

    return app
