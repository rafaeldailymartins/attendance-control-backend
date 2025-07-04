from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.users import service
from app.core import service as core_service
from app.core.config import settings
from app.core.deps import SessionDep
from app.core.exceptions import BaseHTTPException
from app.core.schemas import Token


def get_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = service.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise BaseHTTPException(status_code=400, message="E-mail ou senha incorreta.")
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    return Token(
        access_token=core_service.create_jwt_token(
            user.id, expires_delta=access_token_expires
        )
    )


TokenDep = Annotated[Token, Depends(get_token)]
