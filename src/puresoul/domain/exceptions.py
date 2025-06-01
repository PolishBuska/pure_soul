class DomainException(Exception):
    def __init__(self, message: str):
        self.message = message
        self.type = "DomainException"

class TooManyGenresException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

class AlreadyExistsException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

class NotAuthorizedException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

class NotAuthenticatedException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)
