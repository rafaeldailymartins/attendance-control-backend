FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ARG PROJECT_NAME

WORKDIR /${PROJECT_NAME}/

#Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

ENV PYTHONPATH=/${PROJECT_NAME}

COPY ./scripts ./scripts

COPY ./pyproject.toml ./uv.lock ./alembic.ini ./

COPY ./app ./app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/$PROJECT_NAME/.venv/bin:$PATH"

CMD [ "fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "app/main.py" ]