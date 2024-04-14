#!/bin/sh

# Check if  database is ready
echo "Waiting for database ..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done

echo "Database started"

echo "Apply alembic database migrations"
alembic upgrade head

exec "$@"