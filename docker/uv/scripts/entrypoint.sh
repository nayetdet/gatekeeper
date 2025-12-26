#!/bin/sh
set -e
mkdir -p /app/data /app/config /app/tmp
chown -R app:app /app/data /app/config /app/tmp
su -s /bin/sh app -c "alembic upgrade head"
exec su -s /bin/sh app -c "$*"
