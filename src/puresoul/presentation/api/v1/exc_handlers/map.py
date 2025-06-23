from starlette import status
from typing import Final

from puresoul.domain.exceptions import (
    DomainException,
    AlreadyExistsException,
    TooFewItemsException,
    TooManyGenresException,
    NotAuthorizedException,
    NotAuthenticatedException,
    AlreadyPublic
)

EXC_MAP: Final[dict]= {
        DomainException.__name__: status.HTTP_500_INTERNAL_SERVER_ERROR,
        TooFewItemsException.__name__: status.HTTP_400_BAD_REQUEST,
        TooManyGenresException.__name__: status.HTTP_400_BAD_REQUEST,
        NotAuthorizedException.__name__: status.HTTP_403_FORBIDDEN,
        NotAuthenticatedException.__name__: status.HTTP_401_UNAUTHORIZED,
        AlreadyExistsException.__name__: status.HTTP_409_CONFLICT,
        AlreadyPublic.__name__: status.HTTP_409_CONFLICT
    }