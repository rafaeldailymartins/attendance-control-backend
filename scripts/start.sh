#!/usr/bin/env bash

set -e
set -x

if [ "$ENV" = "local" ]; then
  echo "Starting in local mode..."
  exec fastapi dev --host 0.0.0.0 --port 8000 app/main.py
else
  echo "Starting in $ENV mode..."
  exec fastapi run --host 0.0.0.0 --port 8000 app/main.py
fi