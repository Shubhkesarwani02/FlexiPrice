#!/bin/bash

# FlexiPrice System Test Runner
# This script runs all comprehensive tests and validation checks

set -e

echo "======================================================================"
echo "                  FlexiPrice System Test Suite                       "
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to project root
cd "$(dirname "$0")/.."

echo -e "${BLUE}Step 1: Checking Docker services...${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}Step 2: Running quick validation...${NC}"
python backend/scripts/quick_validation.py

echo ""
echo -e "${BLUE}Step 3: Running comprehensive pytest suite...${NC}"
cd backend
python -m pytest tests/test_comprehensive_system.py -v --tb=short

echo ""
echo -e "${BLUE}Step 4: Running existing unit tests...${NC}"
python -m pytest tests/test_discount_engine.py -v --tb=short
python -m pytest tests/test_batch_processing.py -v --tb=short

echo ""
echo -e "${GREEN}======================================================================"
echo "                     All Tests Completed!                             "
echo "======================================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 to view the storefront"
echo "  2. Open http://localhost:3000/admin to access admin panel"
echo "  3. Check http://localhost:8000/docs for API documentation"
echo ""
