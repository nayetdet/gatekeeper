#!/bin/sh
set -e
mkdir -p /app/data
alembic upgrade head
exec "$@"
