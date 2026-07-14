#!/bin/bash
set -euo pipefail

# Apply the authoritative schema before any application container starts.

echo "Starting database initialization..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST:-postgres}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-postgres}" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready!"

# Set DATABASE_URL if not already set
export DATABASE_URL="${DATABASE_URL:-postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD}@${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-postgres}}"

echo "Running Alembic migrations..."
cd /app
alembic upgrade head
echo "Database migrations completed successfully."

# Create admin user (this is idempotent - won't fail if user already exists)
echo "Creating initial admin user..."
python -m scripts.create_admin

echo "Database initialization completed."
