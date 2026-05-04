# Attendance Control - Backend
![Static Badge](https://img.shields.io/badge/Test-passing-green)
![Static Badge](https://img.shields.io/badge/python-3.12-blue?logo=python)
![Static Badge](https://img.shields.io/badge/docker-28.3-blue?logo=docker)
![Static Badge](https://img.shields.io/badge/postgreSQL-17.5-blue?logo=postgresql)
![Static Badge](https://img.shields.io/badge/uv-0.7.19-blue?logo=uv)

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-br.md)

O **Attendance Control** é um projeto de controle de presença de pessoas em ambientes organizacionais — também conhecido como sistema de ponto.

O sistema foi projetado incialmente como um projeto de faculdade para funcionar em empresas do **Movimento Empresa Júnior** ([MEJ](https://brasiljunior.org.br/conheca-o-mej)), as quais possuiam necessidades de controle de presença específicas, entretanto o projeto está sendo inteiramente refatorado para abranger quaisquer tipos de organizações.

Este repositório refere-se ao backend do sistema **Attendance Control**.

🔗 Projeto principal (frontend + backend): [github.com/rafaeldailymartins/attendance-control](https://github.com/rafaeldailymartins/attendance-control)


## 📋 Dependências

- [Docker](https://www.docker.com/)
- [uv](https://docs.astral.sh/uv/)

## 🚀 Como executar localmente (somente a API)

Primeiramente clone o repoitório e acesse o diretório:

```console
$ git clone https://github.com/rafaeldailymartins/attendance-control-backend.git
$ cd attendance-control-backend
```
Crie um novo arquivo `.env` na raiz do projeto contendo as variáveis de ambiente. Um exemplo pode ser encontrado no arquivo `.env.template`. Lembre-se de alterar as chaves secretas do projeto por razões de segurança — elas estão com o valor `changethis` no template.

Para executar o projeto localmente para o desenvolvimento, com a feature de auto-reload, basta executar o comando docker:

```console
$ docker compose up --watch
```

## 🛠️ Preparando ambiente de desenvolvimento

Por padrão, as dependências são gerenciadas com o [uv](https://docs.astral.sh/uv/). Para instalar as dependências rode:

```console
$ uv sync
```

Este comando irá criar um ambiente virtual do python, então ative-o:

```console
$ source .venv/bin/activate
```

Este projeto utiliza o [pre-commit](https://pre-commit.com/) para rodar comandos antes de realizar commits, instale-o com:

```console
$ pre-commit install --hook-type commit-msg
```

Este projeto utiliza o [ruff](https://docs.astral.sh/ruff/) como linter e formatador de código. Para executar o linter rode:

```console
$ ruff check --fix
```

E para executar o formatador rode:

```console
$ ruff format
```

O projeto também utiliza o [mypy](https://mypy-lang.org/) como type checker. Para executa-lo rode:

```console
$ mypy .
```

Para migrações, o projeto utiliza [alembic](https://alembic.sqlalchemy.org/). Para gerar uma nova migração:

```console
$ ./scripts/gen_migration.sh "migration example"
```

## ⚙️ Rodando os testes

O **Attendance Control** foi projetado para rodar os testes em um banco de dados próprio para homologação.

É possível testar localmente, mas isso irá apagar completamente todos os dados após cada teste. Apagar os dados é necessário para manter o ambiente de homologação limpo e sem interferência de outros testes realizados.

O projeto utiliza [pytest](https://docs.pytest.org/) para testes, mas existe um script bash no projeto para rodar os testes dentro ou fora dos contêiners. Dentro da pasta raiz do projeto, basta rodar:

```console
$ ./scripts/test.sh
```

Também é possível utilizar todas as flags e parametros utilizados pelo pytest junto com o script. Exemplo, para rodar os testes e visualizar no console as saídas do sistema:

```console
$ ./scripts/test.sh -s
```

## 📦 Implantação
Para produção, é necessário primeiro mudar a variável de ambiente `ENV` no arquivo `.env` para:
```env
ENV=production
```

Em seguida deve-se subir o conteinêr docker apenas com o arquivo `docker-compose.yml`:

```console
$ docker compose -f docker-compose.yml up --build
```

## 👨‍💻 Autor

Criado e mantido por:

| [<img src="https://avatars.githubusercontent.com/u/162728324?v=4" width="60px;"/><br /><sub><b>Rafael Daily</b></sub>](https://github.com/rafaeldailymartins)
| :---: |
