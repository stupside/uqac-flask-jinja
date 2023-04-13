from flask import Blueprint, current_app
from flask.cli import with_appcontext

cli_workers = Blueprint('workers', __name__, cli_group=None)


@cli_workers.cli.command("worker")
@with_appcontext
def payment_worker():
    current_app.logger.info("Starting payment background worker")

    from src.application.configuration import AbstractConfig

    redis = AbstractConfig(current_app.config).REDIS_CONNECTION

    with redis:
        from rq import Worker, Queue

        queue = Queue("payments", connection=redis)

        worker = Worker([queue], connection=redis)

        worker.work()
