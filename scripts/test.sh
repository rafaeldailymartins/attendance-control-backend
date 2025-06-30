#!/usr/bin/env bash

set -e

# Detects if we are outside a container
if [ -z "$IS_CONTAINER" ] || [ "$IS_CONTAINER" = "false" ] || [ "$IS_CONTAINER" = "False" ]; then
    export POSTGRES_SERVER=localhost
fi
echo "Using database on server: $POSTGRES_SERVER"

# Abort if is production
if [ "$ENV" = "production" ]; then
    echo
    echo -e "\033[1;31mERROR:\033[0m This script cannot be run in the production environment."
    exit 1
fi

# Confirm to continue
if [ "$ENV" != "staging" ]; then
    echo
    echo -e "\033[1;33mWARNING:\033[0m At the end of the tests, all data in the database will be deleted."

    read -rp "Do you want to continue? (y/N): " confirm
    confirm=${confirm,,}

    if [[ "$confirm" == "y" || "$confirm" == "yes" ]]; then
        echo "Proceeding with tests..."
        echo
    else
        echo "Aborting test run."
        exit 1
    fi
fi

set -x
pytest "$@"
