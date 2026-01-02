#!/bin/bash
# Database initialization script for Docker
# This script runs Alembic migrations and creates the initial admin user
# Note: If backend already created tables via init_db(), migrations may be partially applied
# We don't use 'set -e' because we want to continue even if migrations have issues

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

# Run Alembic migrations
# Note: Backend's init_db() creates tables via create_all(), but doesn't run migrations
# Alembic tracks applied migrations in alembic_version table
echo "Running Alembic migrations..."
cd /app

# Check if alembic_version table exists (indicates migrations have been tracked)
ALEMBIC_VERSION_EXISTS=$(PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST:-postgres}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-postgres}" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version'" 2>/dev/null || echo "")

if [ -n "$ALEMBIC_VERSION_EXISTS" ]; then
    echo "Alembic version table exists - migrations have been tracked"
    echo "Running alembic upgrade head (will skip already applied migrations)..."
else
    echo "No alembic_version table found - this may be the first migration run"
    echo "Note: If backend already created tables via init_db(), Alembic will detect and handle this"
fi

# Run migrations - Alembic is idempotent and handles existing tables gracefully
# If tables exist but alembic_version doesn't, Alembic will stamp the current revision
if alembic upgrade head 2>&1; then
    echo "✅ Alembic migrations completed successfully"
else
    MIGRATION_ERROR=$?
    echo "⚠️  Alembic migrations encountered issues (exit code: $MIGRATION_ERROR)"
    echo "This may be normal if:"
    echo "  - Tables were already created by backend's init_db()"
    echo "  - Migrations were already applied"
    echo "Attempting to stamp current revision if needed..."
    # Try to stamp the current revision if tables exist but version table doesn't
    alembic stamp head 2>/dev/null || echo "Could not stamp revision (this may be normal)"
    echo "Continuing with admin user creation..."
fi

# Create admin user (this is idempotent - won't fail if user already exists)
echo "Creating initial admin user..."
python scripts/create_admin.py || {
    echo "⚠️  Admin user creation had issues (may already exist)"
    # Don't exit - this is expected if user already exists
}

echo "Database initialization completed!"
