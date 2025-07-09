from fastapi import APIRouter, Depends, status

from app.api.app_config import crud as app_config_crud
from app.api.users import crud
from app.api.users.deps import TokenDep
from app.api.users.schemas import UserCreate, UserResponse, UserUpdate
from app.core.crud import db_delete
from app.core.deps import CurrentUserDep, SessionDep, check_admin
from app.core.exceptions import BaseHTTPException, ForbiddenException
from app.core.schemas import Message, Token

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login")
def login(token: TokenDep) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    return token


@router.post("/login/swagger", include_in_schema=False)
def login_swagger(token: TokenDep):
    """
    Used only by swagger.
    OAuth2 compatible token login, get an access token for future requests
    """
    return token.model_dump()


@router.post("/me", response_model=UserResponse)
def get_current_user(current_user: CurrentUserDep):
    """
    Get current authenticated user.
    """
    return current_user


@router.post("/", response_model=UserResponse, dependencies=[Depends(check_admin)])
def create_new_user(session: SessionDep, body: UserCreate):
    """
    Create new user
    """
    user = crud.get_user_by_email(session=session, email=body.email)
    if user:
        raise BaseHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Já existe um usuário com este e-mail no sistema.",
        )

    if body.role_id is not None:
        role = app_config_crud.get_role_by_id(session, body.role_id)
        if not role:
            raise BaseHTTPException(
                status_code=status.HTTP_404_NOT_FOUND, message="Cargo não encontrado"
            )

    user_create = UserCreate.model_validate(body)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/", response_model=list[UserResponse], dependencies=[Depends(check_admin)])
def list_users(session: SessionDep):
    """
    Lists all users
    """
    return crud.list_users(session)


@router.get(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(check_admin)]
)
def get_user(session: SessionDep, user_id: int):
    """
    Get user by id
    """
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Usuário não encontrado"
        )
    return user


@router.patch(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(check_admin)]
)
def update_user(session: SessionDep, user_id: int, body: UserUpdate):
    """
    Update a user
    """
    if body.email is not None:
        user = crud.get_user_by_email(session=session, email=body.email)
        if user and user.id != user_id:
            raise BaseHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Já existe um usuário com este e-mail no sistema.",
            )
    if body.role_id is not None:
        role = app_config_crud.get_role_by_id(session, body.role_id)
        if not role:
            raise BaseHTTPException(
                status_code=status.HTTP_404_NOT_FOUND, message="Cargo não encontrado"
            )

    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Usuário não encontrado"
        )
    crud.update_user(session, user, body)
    return user


@router.delete("/{user_id}", dependencies=[Depends(check_admin)])
def delete_user(
    session: SessionDep, user_id: int, current_user: CurrentUserDep
) -> Message:
    """
    Delete a user.
    """
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Usuário não encontrado"
        )
    if user.id == current_user.id:
        raise ForbiddenException("Não é possível deletar a si mesmo")
    db_delete(session, user)
    return Message(message="Usuário deletado com sucesso")
