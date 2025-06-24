from typing import Annotated, Any, Literal, Self
import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    model_validator,
)


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
    ENV: Literal["local", "staging", "production"] = "local"

    # FastAPI parameters
    TITLE: str
    VERSION: str
    DESCRIPTION: str

    # First admin settings
    ADMIN_ROLE_NAME: str = "admin"
    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str

    # Default App Config
    DEFAULT_MINUTES_EARLY: int = 15
    DEFAULT_MINUTES_LATE: int = 15

    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # CORS
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

    # Check secrets
    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENV == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("FIRST_ADMIN_PASSWORD", self.FIRST_ADMIN_PASSWORD)

        return self


settings = Settings()  # type: ignore
