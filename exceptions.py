import inspect

from decorator import decorate


class BaseServiceException(Exception):
    detail: str

    def __init__(self, detail: str):
        self.detail = detail


class ObjectNotFoundException(BaseServiceException):
    pass


class DatabaseException(Exception):
    pass


async def _database_exception_wrapper(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        raise DatabaseException(e)


def database_exception_wrapper(func):
    return decorate(func, _database_exception_wrapper)
