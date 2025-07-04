#!/usr/bin/env bash

set -e

if [ -z "$1" ]; then
  echo "Error: this script requires 1 argument"
  echo "Usage: ./gen_migration.sh [MESSAGE]"
  exit 1
fi

#Detects if we are outside a container
if [ -z "$IS_CONTAINER" ] || [ "$IS_CONTAINER" = "false" ] || [ "$IS_CONTAINER" = "False" ]; then
    export POSTGRES_SERVER=localhost
fi
echo "Using database on server: $POSTGRES_SERVER"

set -x
#Generate a migration
alembic revision --autogenerate -m "$1"
