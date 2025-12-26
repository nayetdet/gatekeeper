#!/bin/sh
set -e
mkdir -p /app/data /app/config /app/tmp
alembic upgrade head
exec "$@"
