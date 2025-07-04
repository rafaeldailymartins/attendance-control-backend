from fastapi import APIRouter

from app.api.users.deps import TokenDep
from app.api.users.schemas import UserResponse
from app.core.deps import CurrentUserDep

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login")
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
