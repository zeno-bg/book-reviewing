class BaseServiceException(Exception):
    detail: str

    def __init__(self, detail: str):
        self.detail = detail


class ObjectNotFoundException(BaseServiceException):
    pass
