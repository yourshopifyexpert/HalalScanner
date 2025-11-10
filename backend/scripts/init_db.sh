#!/bin/bash

# Initialize database with tables and seed data

echo "Initializing HalalScanner database..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run database initialization
python -c "from app.database import init_db; init_db()"

echo "Database tables created."

# Seed data
echo "Seeding initial data..."
python app/seed_data.py

echo "Database initialization complete!"
