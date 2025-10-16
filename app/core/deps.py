from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_session
from app.core.exceptions import Forbidden, NotFound, Unauthorized
from app.core.models import User
from app.core.schemas import PaginationParams, TokenPayload

PaginationDep = Annotated[PaginationParams, Depends()]
SessionDep = Annotated[Session, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/swagger", auto_error=False)


def get_current_user(
    session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
):
    if not token:
        raise Unauthorized()
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise Forbidden("Não foi possível validar as credenciais")
    user = session.get(User, token_data.sub)
    if not user:
        raise NotFound("Usuário não encontrado.")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def check_admin(current_user: CurrentUserDep):
    if (
        current_user.role is not None
        and current_user.role.name == settings.ADMIN_ROLE_NAME
    ):
        return True

    raise Forbidden()
