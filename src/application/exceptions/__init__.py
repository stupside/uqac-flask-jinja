class Error:
    code: str
    message: str

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message.replace("\"", "'")

    def __dict__(self):
        return {
            "code": self.code,
            "message": self.message
        }


class ApplicationError(Exception):
    errors: dict[str, list[Error]] = {}

    def __init__(self, code: int, errors: dict[str, list[Error]]):
        self.code = code
        self.errors = errors

    def to_dict(self):
        return {
            "errors": {
                name.lower(): list({"code": error.code, "message": error.message} for error in errors)
                for name, errors in self.errors.items()
            }
        }
