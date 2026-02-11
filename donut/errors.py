class DonutAPIError(Exception):
    pass


class UnauthorizedError(DonutAPIError):
    pass


class NotFoundError(DonutAPIError):
    pass


class ServerError(DonutAPIError):
    pass

