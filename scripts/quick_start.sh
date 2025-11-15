#!/bin/bash

# FlexiPrice - Quick Start & Verification Script
# This script sets up and verifies your FlexiPrice installation

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         FlexiPrice - Dynamic Pricing System                    ║"
echo "║              Quick Start & Verification                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Docker
echo -e "${BLUE}Step 1: Checking Docker...${NC}"
if docker ps >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${YELLOW}⚠ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Step 2: Start Services
echo ""
echo -e "${BLUE}Step 2: Starting Docker services...${NC}"
docker-compose up -d
sleep 5

# Step 3: Check Services
echo ""
echo -e "${BLUE}Step 3: Verifying services...${NC}"
docker-compose ps

# Step 4: Wait for Backend
echo ""
echo -e "${BLUE}Step 4: Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Step 5: Run Validation
echo ""
echo -e "${BLUE}Step 5: Running system validation...${NC}"
python3 backend/scripts/quick_validation.py

# Step 6: Instructions
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Backend API:${NC} http://localhost:8000"
echo -e "${GREEN}✓ API Docs:${NC}    http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}To start the frontend:${NC}"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Then access:${NC}"
echo "  • Storefront: http://localhost:3000"
echo "  • Admin:      http://localhost:3000/admin"
echo "  • Analytics:  http://localhost:3000/admin/analytics"
echo ""
echo -e "${BLUE}Optional - Train ML Model:${NC}"
echo "  python3 backend/scripts/train_model.py"
echo ""
echo -e "${BLUE}Run full tests:${NC}"
echo "  ./scripts/run_all_tests.sh"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Read TEST_RESULTS.md for detailed test information           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
