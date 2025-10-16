from app.core.schemas import ApiError


def error_responses(codes: list[int]):
    return {code: {"model": ApiError} for code in codes}


CURRENT_USER_ERRORS = error_responses([401, 403, 404])
BAD_REQUEST_ERROR = error_responses([400])
