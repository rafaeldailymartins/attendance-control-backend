from fastapi import APIRouter, Depends, status

from app.api.users import crud
from app.api.users.deps import TokenDep
from app.api.users.schemas import UserCreate, UserResponse, UserUpdate
from app.core.deps import CurrentUserDep, SessionDep, check_admin
from app.core.exceptions import BaseHTTPException
from app.core.schemas import Token

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login", response_model=Token)
def login(token: TokenDep):
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
            status_code=400,
            message="Já existe um usuário com este e-mail no sistema.",
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
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Usuário não encontrado"
        )
    crud.update_user(session, user, body)
    return user
