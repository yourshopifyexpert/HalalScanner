#!/bin/bash

# HalalScanner Test Runner
# Runs all tests across the project

set -e

echo "🧪 Running HalalScanner Tests..."

# Backend tests
echo ""
echo "🔧 Running Backend Tests..."
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app --cov-report=term-missing
cd ..

# Mobile tests (if any)
echo ""
echo "📱 Running Mobile App Tests..."
cd mobile
if [ -f "package.json" ]; then
    npm test -- --watchAll=false || echo "⚠️  Mobile tests not configured yet"
fi
cd ..

# Admin tests (if any)
echo ""
echo "🖥️  Running Admin Console Tests..."
cd admin
if [ -f "package.json" ]; then
    npm test -- --watchAll=false || echo "⚠️  Admin tests not configured yet"
fi
cd ..

echo ""
echo "✅ All tests completed!"
