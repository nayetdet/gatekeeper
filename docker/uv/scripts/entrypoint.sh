#!/bin/sh
set -e
mkdir -p /app/data /app/tmp
alembic upgrade head
exec "$@"
