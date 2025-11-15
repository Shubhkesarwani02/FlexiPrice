#!/bin/bash

# Database Setup Script for FlexiPrice
# This script helps set up the database with proper migrations

echo "🚀 FlexiPrice Database Setup"
echo "=============================="

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo "✅ Created .env file. Please update it with your configuration."
    exit 1
fi

echo ""
echo "Step 1: Starting Docker services (Postgres + Redis)..."
docker-compose up -d postgres redis

echo ""
echo "Step 2: Waiting for Postgres to be ready..."
sleep 5

echo ""
echo "Step 3: Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo ""
echo "Step 4: Generating Prisma Client..."
prisma generate

echo ""
echo "Step 5: Pushing Prisma schema to database..."
prisma db push

echo ""
echo "✅ Database setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Start the backend: uvicorn app.main:app --reload"
echo "   2. Visit API docs: http://localhost:8000/docs"
