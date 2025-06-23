from fastapi import HTTPException
from starlette.requests import Request

from puresoul.domain.exceptions import DomainException
from .map import EXC_MAP

def handle_exceptions(req: Request, exc: DomainException) -> None:
    if isinstance(exc, DomainException):
        response = HTTPException(
            detail={
                'message': exc.message,
                'type': exc.type,
            }
            ,
            status_code=EXC_MAP[exc.__class__.__name__],
        )
        raise response
    else:
        raise HTTPException(
            detail=f'Unknown exception {str(exc)}',
            status_code=500,
        )
