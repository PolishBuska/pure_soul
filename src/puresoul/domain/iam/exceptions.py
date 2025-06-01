from ..exceptions import DomainException

class NotAuthorizedException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

class NotOldEnoughException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)
