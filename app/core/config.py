from typing import Annotated, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, BeforeValidator, computed_field


def parse_cors(v: Any) -> list[str]:
    if isinstance(v, str):
        return [i.strip() for i in v.split(",")]
    if isinstance(v, list):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str

    ADMIN_ROLE_NAME: str = "admin"
    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str

    DEFAULT_MINUTES_EARLY: int = 15
    DEFAULT_MINUTES_LATE: int = 15

    DATABASE_URL: str

    FRONTEND_HOST: AnyUrl = AnyUrl("http://localhost:5173")
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            str(self.FRONTEND_HOST)
        ]


settings = Settings()  # type: ignore
