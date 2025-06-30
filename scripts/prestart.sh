#! /usr/bin/env bash

set -e

#Detects if we are outside a container
if [ -z "$IS_CONTAINER" ] || [ "$IS_CONTAINER" = "false" ] || [ "$IS_CONTAINER" = "False" ]; then
    export POSTGRES_SERVER=localhost
fi
echo "Using database on server: $POSTGRES_SERVER"

set -x
# Run migrations
alembic upgrade head

# Create initial data in DB
python -m app.init_data