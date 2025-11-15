#!/bin/bash

# Start Frontend Development Server

echo "🚀 Starting FlexiPrice Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found"
    echo "Creating from .env.example..."
    cp .env.example .env.local
    echo "✓ Please update .env.local with your configuration"
    echo ""
fi

# Start the development server
echo "🌐 Starting Next.js development server on http://localhost:3000"
echo ""
npm run dev
