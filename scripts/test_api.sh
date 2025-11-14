#!/bin/bash

# Test script to verify API endpoints are working
# Run this after starting the server with docker-compose up or uvicorn

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"

echo "🧪 Testing FlexiPrice API Endpoints"
echo "===================================="
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Check..."
curl -s "$BASE_URL/health" | jq
echo ""

# Test 2: Create a Product
echo "2️⃣  Creating a test product..."
PRODUCT_RESPONSE=$(curl -s -X POST "$API_URL/admin/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST-001",
    "name": "Test Product",
    "description": "A test product for API testing",
    "category": "Test",
    "base_price": 99.99
  }')
echo $PRODUCT_RESPONSE | jq
PRODUCT_ID=$(echo $PRODUCT_RESPONSE | jq -r '.id')
echo "Created Product ID: $PRODUCT_ID"
echo ""

# Test 3: List Products
echo "3️⃣  Listing all products..."
curl -s "$API_URL/admin/products" | jq
echo ""

# Test 4: Get Product by ID
echo "4️⃣  Getting product by ID..."
curl -s "$API_URL/admin/products/$PRODUCT_ID" | jq
echo ""

# Test 5: Create Inventory Batch
echo "5️⃣  Creating inventory batch..."
BATCH_RESPONSE=$(curl -s -X POST "$API_URL/admin/inventory" \
  -H "Content-Type: application/json" \
  -d "{
    \"product_id\": $PRODUCT_ID,
    \"batch_code\": \"BATCH-001\",
    \"quantity\": 100,
    \"expiry_date\": \"2025-12-31\"
  }")
echo $BATCH_RESPONSE | jq
BATCH_ID=$(echo $BATCH_RESPONSE | jq -r '.id')
echo "Created Batch ID: $BATCH_ID"
echo ""

# Test 6: List Inventory Batches
echo "6️⃣  Listing all inventory batches..."
curl -s "$API_URL/admin/inventory" | jq
echo ""

# Test 7: Get Product Batches
echo "7️⃣  Getting batches for product $PRODUCT_ID..."
curl -s "$API_URL/admin/inventory/product/$PRODUCT_ID" | jq
echo ""

# Test 8: Get Products with Discounts
echo "8️⃣  Getting products with discount info..."
curl -s "$API_URL/admin/products/with-discounts" | jq
echo ""

# Test 9: Get Expiring Batches
echo "9️⃣  Getting expiring batches (within 30 days)..."
curl -s "$API_URL/admin/inventory/expiring?days=30" | jq
echo ""

echo "✅ API Tests Complete!"
echo ""
echo "📝 Cleanup (optional):"
echo "   Delete batch: curl -X DELETE $API_URL/admin/inventory/$BATCH_ID"
echo "   Delete product: curl -X DELETE $API_URL/admin/products/$PRODUCT_ID"
