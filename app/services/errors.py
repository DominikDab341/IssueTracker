"""Błędy przypadków użycia; ich reprezentację HTTP ustala warstwa API."""


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class InvalidInputError(Exception):
    def __init__(self, message: str, *, field: str | None = None):
        super().__init__(message)
        self.field = field
