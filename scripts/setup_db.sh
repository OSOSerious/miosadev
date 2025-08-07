#!/bin/bash
# scripts/setup_db.sh

echo "=€ Setting up MIOSA database..."

# Database credentials
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASSWORD="${POSTGRES_PASSWORD:-password}"
DB_NAME="${POSTGRES_DB:-miosa}"
DB_HOST="${POSTGRES_SERVER:-localhost}"

# Create database
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database already exists"

# Run your SQL schemas
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f scripts/01_base_schema.sql
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f scripts/02_base44_additions.sql

echo " Database setup complete!"