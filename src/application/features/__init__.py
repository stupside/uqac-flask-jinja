from functools import singledispatch

from src.application.exceptions import Error, ApplicationError


def is_valid_string(string: str) -> bool:
    return bool(string and string.split())


class Mediator:

    @staticmethod
    def dispatch(*args):
        failure = Mediator.validate(*args)

        if failure:
            (name, message, code) = failure

            error = ApplicationError(code, {name: message})

            raise error

        return Mediator.handle(*args)

    @staticmethod
    @singledispatch
    def validate(*args) -> tuple[str, list[Error], int] | None:
        raise NotImplementedError(f'Unsupported type : {type(args)}')

    @staticmethod
    @singledispatch
    def handle(*args):
        raise NotImplementedError(f'Unsupported type : {type(args)}')
