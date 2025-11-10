#!/bin/bash

# HalalScanner Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up HalalScanner Development Environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed!"

# Setup backend
echo ""
echo "🔧 Setting up Backend..."
cd backend

if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your configuration!"
fi

if [ ! -d venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

cd ..

# Setup mobile app
echo ""
echo "📱 Setting up Mobile App..."
cd mobile

if [ ! -d node_modules ]; then
    echo "Installing npm dependencies..."
    npm install
else
    echo "Dependencies already installed, skipping..."
fi

cd ..

# Setup admin console
echo ""
echo "🖥️  Setting up Admin Console..."
cd admin

if [ ! -d node_modules ]; then
    echo "Installing npm dependencies..."
    npm install
else
    echo "Dependencies already installed, skipping..."
fi

cd ..

# Start Docker services
echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis elasticsearch rabbitmq

echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo ""
echo "💾 Initializing database..."
cd backend
source venv/bin/activate
python app/seed_data.py
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Edit backend/.env with your API keys"
echo "   2. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   3. Start mobile app: cd mobile && npm start"
echo "   4. Start admin console: cd admin && npm start"
echo ""
echo "   Or use Docker Compose to start everything:"
echo "   docker-compose up"
echo ""
echo "🎉 Happy coding!"
