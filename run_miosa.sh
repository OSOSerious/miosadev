#!/bin/bash

echo "🤖 Starting MIOSA AI Application Builder..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check database
echo "Checking database..."
psql -U postgres -d miosa -c "SELECT COUNT(*) FROM users;" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Setting up database..."
    psql -U postgres -c "CREATE DATABASE miosa;" 2>/dev/null
    psql -U postgres -d miosa -f scripts/simple_schema.sql
fi

# Run the CLI
echo ""
echo "Starting MIOSA CLI..."
echo "="*60
python -m app.cli