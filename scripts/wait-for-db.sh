#!/bin/sh

set -e

HOST="$1"
shift
CMD="$@"

MAX_RETRIES=30
RETRY_INTERVAL=2


retries=0
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
    retries=$((retries + 1))
    if [ $retries -ge $MAX_RETRIES ]; then
        echo "Error: PostgreSQL is not available after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "PostgreSQL is unavailable - sleeping (attempt $retries/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
done

echo "PostgreSQL is up - executing command"
exec $CMD

