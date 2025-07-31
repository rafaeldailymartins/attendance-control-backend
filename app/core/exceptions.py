from typing import Any

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Base exception for all HTPP exceptions."""

    def __init__(self, status_code: int, message: str, extra: Any = None):
        super().__init__(
            status_code=status_code, detail={"message": message, "extra": extra}
        )


class InternalServerErrorException(BaseHTTPException):
    """Base exception for internal server error."""

    def __init__(self, message: str = "Ocorreu um erro no servidor", extra: Any = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            extra=extra,
        )


class ForbiddenException(BaseHTTPException):
    """Base exception for internal server error."""

    def __init__(self, message: str = "Acesso negado", extra: Any = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, message=message, extra=extra
        )
