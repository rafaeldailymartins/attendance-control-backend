from fastapi import status


class BaseHTTPException(Exception):
    """Base exception for all HTTP exceptions."""

    def __init__(self, status_code: int, message: str, metadata: None = None):
        """Base exception for all HTTP exceptions."""
        self.status_code = status_code
        self.message = message
        self.metadata = metadata


class InternalServerError(BaseHTTPException):
    """Base exception for internal server error."""

    def __init__(self, message: str = "Ocorreu um erro no servidor"):
        """Internal Server Error (HTTP 500)."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message
        )


class Forbidden(BaseHTTPException):
    """Base exception for forbbiden."""

    def __init__(self, message: str = "Acesso negado."):
        """Forbidden (HTTP 403)."""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class Unauthorized(BaseHTTPException):
    """Base exception for unauthorized."""

    def __init__(self, message: str = "Usuário não autenticado"):
        """Unauthorized (HTTP 401)."""
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class NotFound(BaseHTTPException):
    """Base exception for not found."""

    def __init__(self, message: str = "Usuário não autenticado"):
        """Not found (HTTP 404)."""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class BadRequest(BaseHTTPException):
    """Base exception for bad request."""

    def __init__(self, message: str = "Usuário não autenticado"):
        """Bad request (HTTP 400)."""
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message)
