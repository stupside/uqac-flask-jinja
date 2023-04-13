from flask import Blueprint

from src.cli.manage import cli_manage
from src.cli.workers import cli_workers

app_cli = Blueprint('manage', __name__, cli_group=None)

app_cli.register_blueprint(cli_manage, cli_group=None)
app_cli.register_blueprint(cli_workers, cli_group=None)
