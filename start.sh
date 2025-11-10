#!/bin/sh
set -e

# Use Railway's PORT variable or default to 8000
PORT=${PORT:-8000}

echo "Starting HalalScanner API on port $PORT"

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
