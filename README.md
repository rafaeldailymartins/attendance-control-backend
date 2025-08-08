# Attendance Control - Backend
![Static Badge](https://img.shields.io/badge/Test-passing-green)
![Static Badge](https://img.shields.io/badge/python-3.12-blue?logo=python)
![Static Badge](https://img.shields.io/badge/docker-28.3-blue?logo=docker)
![Static Badge](https://img.shields.io/badge/postgreSQL-17.5-blue?logo=postgresql)
![Static Badge](https://img.shields.io/badge/uv-0.7.19-blue?logo=uv)

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-br.md)

**Attendance Control** is a clock in and out system for organizational environments.

The system was initially designed as a college project to serve companies from [**Junior Enterprises Movement**](https://brasiljunior.org.br/conheca-o-mej), which had specific attendance control needs. However, it is now being completely refactored to support any type of organization.

This repository refers to the backend of the **Attendance Control** system.

🔗 Main project (frontend + backend): [github.com/rafaeldailymartins/attendance-control](https://github.com/rafaeldailymartins/attendance-control)

## 📋 Dependencies

- [Docker](https://www.docker.com/)
- [uv](https://docs.astral.sh/uv/)

## 🚀 Running locally (API only)

First, clone the repository and navigate to the project directory:

```console
$ git clone https://github.com/rafaeldailymartins/attendance-control-backend.git
$ cd attendance-control-backend
```

Create a new `.env` file in the project root containing the required environment variables.
You can use the `.env.template` file as a reference. Remember to change all secret keys for security reasons — in the template they are set to `changethis`.

To run the project locally for development with auto-reload enabled, simply run:

```console
$ docker compose up --watch
```

## 🛠️ Setting up the development environment

By default, dependencies are managed with [uv](https://docs.astral.sh/uv/). To install them, run:

```console
$ uv sync
```

This will create a Python virtual environment. Activate it with:

```console
$ source .venv/bin/activate
```

This project uses [pre-commit](https://pre-commit.com/)  to run checks before commits. Install it with:

```console
$ pre-commit install --hook-type commit-msg
```

This project also uses [ruff](https://docs.astral.sh/ruff/) as a linter and code formatter.
Run the linter with:

```console
$ ruff check --fix
```

Run the code formatter with:

```console
$ ruff format
```

For type checking, the project uses [mypy](https://mypy-lang.org/). To run it:

```console
$ mypy .
```

## ⚙️ Running tests

**Attendance Control** is designed to run tests against a dedicated staging database.

You can run tests locally, but keep in mind that all data will be permanently erased after each test run.
This cleanup is necessary to keep the staging environment clean and free from interference between tests.

The project uses [pytest](https://docs.pytest.org/) for testing, but also provides a bash script to run tests either inside or outside Docker containers.
From the project root, run:

```console
$ ./scripts/test.sh
```

You can also pass any flags and parameters supported by pytest. For example, to run tests and see outputs in the console:

```console
$ ./scripts/test.sh -s
```

## 📦 Deployment
For production, first change the `ENV` environment variable in your `.env` file to:
```env
ENV=production
```

Then start the Docker container using only the `docker-compose.yml` file:

```console
$ docker compose -f docker-compose.yml up --build
```

## 👨‍💻 Author

Created and maintained by:

| [<img src="https://avatars.githubusercontent.com/u/162728324?v=4" width="60px;"/><br /><sub><b>Rafael Daily</b></sub>](https://github.com/rafaeldailymartins)
| :---: |
