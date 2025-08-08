from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Base exception for all HTPP exceptions."""

    def __init__(self, status_code: int, message: str):
        detail = {"message": message}
        super().__init__(status_code=status_code, detail=detail)


class InternalServerError(BaseHTTPException):
    """Base exception for internal server error."""

    def __init__(self, message: str = "Ocorreu um erro no servidor"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message
        )


class Forbidden(BaseHTTPException):
    """Base exception for forbbiden."""

    def __init__(self, message: str = "Acesso negado."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class IncorretEmailOrPassword(BaseHTTPException):
    """Base exception when the email or password is incorrect."""

    def __init__(self, message: str = "E-mail ou senha incorreta."):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class Unauthenticated(BaseHTTPException):
    """Base exception for unauthenticated."""

    def __init__(self, message: str = "Usuário não autenticado"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class RoleNotFound(BaseHTTPException):
    """Base exception when role was not found."""

    def __init__(self, message: str = "Cargo não encontrado."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class UserNotFound(BaseHTTPException):
    """Base exception when user was not found."""

    def __init__(self, message: str = "Usuário não encontrado."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class ShiftNotFound(BaseHTTPException):
    """Base exception when shift was not found."""

    def __init__(self, message: str = "Turno não encontrado."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class AttendanceNotFound(BaseHTTPException):
    """Base exception when attendance was not found."""

    def __init__(self, message: str = "Registro não encontrado."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class DayOffNotFound(BaseHTTPException):
    """Base exception when day off was not found."""

    def __init__(self, message: str = "Dia livre não encontrado."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)
