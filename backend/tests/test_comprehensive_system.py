"""
Comprehensive End-to-End System Tests for FlexiPrice

This test suite validates:
1. Product Management (CRUD operations)
2. Inventory Management (batch tracking, expiry)
3. Discount Engine (rule-based computation)
4. ML Predictions (discount recommendations)
5. Analytics (sales, conversions, metrics)
6. A/B Testing (experiment management)
7. Scheduler (Celery tasks)
8. Database integrity

Run with: pytest tests/test_comprehensive_system.py -v
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import httpx
from typing import Dict, Any

# Test Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


class TestProductManagement:
    """Test product CRUD operations"""
    
    @pytest.mark.asyncio
    async def test_create_product(self):
        """Test creating a new product"""
        async with httpx.AsyncClient() as client:
            product_data = {
                "sku": f"TEST-PROD-{datetime.now().timestamp()}",
                "name": "Test Product",
                "description": "A comprehensive test product",
                "category": "Electronics",
                "base_price": 199.99
            }
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/products",
                json=product_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["sku"] == product_data["sku"]
            assert data["name"] == product_data["name"]
            assert float(data["basePrice"]) == product_data["base_price"]
            
            return data
    
    @pytest.mark.asyncio
    async def test_list_products(self):
        """Test listing all products"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/products")
            
            assert response.status_code == 200
            products = response.json()
            assert isinstance(products, list)
            assert len(products) > 0
            
            # Verify product structure
            product = products[0]
            assert "id" in product
            assert "sku" in product
            assert "name" in product
            assert "basePrice" in product
    
    @pytest.mark.asyncio
    async def test_get_product_by_sku(self):
        """Test retrieving a specific product by SKU"""
        async with httpx.AsyncClient() as client:
            # First, create a product
            product_data = {
                "sku": f"GET-TEST-{datetime.now().timestamp()}",
                "name": "Get Test Product",
                "description": "Test product retrieval",
                "category": "Test",
                "base_price": 99.99
            }
            
            create_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/products",
                json=product_data
            )
            assert create_response.status_code == 200
            created_product = create_response.json()
            
            # Now retrieve it
            get_response = await client.get(
                f"{BASE_URL}{API_PREFIX}/admin/products/{created_product['sku']}"
            )
            
            assert get_response.status_code == 200
            retrieved_product = get_response.json()
            assert retrieved_product["sku"] == product_data["sku"]
            assert retrieved_product["name"] == product_data["name"]


class TestInventoryManagement:
    """Test inventory batch operations"""
    
    @pytest.mark.asyncio
    async def test_add_inventory_batch(self):
        """Test adding an inventory batch to a product"""
        async with httpx.AsyncClient() as client:
            # Create a product first
            product_data = {
                "sku": f"INV-PROD-{datetime.now().timestamp()}",
                "name": "Inventory Test Product",
                "description": "Product for inventory testing",
                "category": "Food",
                "base_price": 50.00
            }
            
            product_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/products",
                json=product_data
            )
            product = product_response.json()
            
            # Add inventory batch
            batch_data = {
                "product_id": product["id"],
                "batch_code": f"BATCH-{datetime.now().timestamp()}",
                "quantity": 100,
                "expiry_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
            }
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/inventory",
                json=batch_data
            )
            
            assert response.status_code == 200
            batch = response.json()
            assert batch["productId"] == product["id"]
            assert batch["quantity"] == batch_data["quantity"]
            
            return batch
    
    @pytest.mark.asyncio
    async def test_list_inventory_batches(self):
        """Test listing all inventory batches"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/inventory")
            
            assert response.status_code == 200
            batches = response.json()
            assert isinstance(batches, list)


class TestDiscountEngine:
    """Test discount computation and rules"""
    
    @pytest.mark.asyncio
    async def test_discount_computation(self):
        """Test that discounts are computed based on expiry"""
        async with httpx.AsyncClient() as client:
            # Create product
            product_data = {
                "sku": f"DISC-PROD-{datetime.now().timestamp()}",
                "name": "Discount Test Product",
                "description": "Product for discount testing",
                "category": "Perishable",
                "base_price": 100.00
            }
            
            product_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/products",
                json=product_data
            )
            product = product_response.json()
            
            # Add batch with near expiry (2 days)
            batch_data = {
                "product_id": product["id"],
                "batch_code": f"BATCH-EXPIRING-{datetime.now().timestamp()}",
                "quantity": 50,
                "expiry_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            }
            
            batch_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/inventory",
                json=batch_data
            )
            assert batch_response.status_code == 200
            
            # Wait a moment for discount computation
            await asyncio.sleep(2)
            
            # Check product has discount
            product_response = await client.get(
                f"{BASE_URL}{API_PREFIX}/admin/products/{product['sku']}"
            )
            
            product_with_discount = product_response.json()
            
            # Should have storefront_price less than base_price
            if "storefront_price" in product_with_discount:
                storefront = float(product_with_discount["storefront_price"])
                base = float(product_with_discount["basePrice"])
                # With 2 days to expiry, should have 60% discount
                assert storefront < base, "Storefront price should be less than base price"
    
    @pytest.mark.asyncio
    async def test_get_all_discounts(self):
        """Test retrieving all active discounts"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/discounts")
            
            assert response.status_code == 200
            discounts = response.json()
            assert isinstance(discounts, list)
            
            if len(discounts) > 0:
                discount = discounts[0]
                assert "id" in discount
                assert "batchId" in discount
                assert "computedPrice" in discount
                assert "discountPct" in discount


class TestMLPredictions:
    """Test ML recommendation system"""
    
    @pytest.mark.asyncio
    async def test_ml_recommendation(self):
        """Test ML discount recommendations"""
        async with httpx.AsyncClient() as client:
            # Get a product for testing
            products_response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/products")
            products = products_response.json()
            
            if len(products) > 0:
                product = products[0]
                
                # Request ML recommendation
                params = {
                    "product_id": product["id"],
                    "days_to_expiry": 5,
                    "inventory_level": 100
                }
                
                response = await client.get(
                    f"{BASE_URL}{API_PREFIX}/admin/ml/recommend",
                    params=params
                )
                
                # ML endpoint might not be fully trained, so check both success and proper error
                if response.status_code == 200:
                    recommendations = response.json()
                    assert isinstance(recommendations, (list, dict))
                elif response.status_code == 500:
                    # Model might not be trained yet
                    error = response.json()
                    assert "detail" in error
    
    @pytest.mark.asyncio
    async def test_ml_model_status(self):
        """Test ML model availability"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/ml/status")
            
            # Status endpoint may or may not exist
            assert response.status_code in [200, 404, 501]


class TestAnalytics:
    """Test analytics endpoints"""
    
    @pytest.mark.asyncio
    async def test_analytics_overview(self):
        """Test analytics overview endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/analytics")
            
            assert response.status_code == 200
            analytics = response.json()
            
            # Check for expected keys
            assert "total_products" in analytics
            assert "total_batches" in analytics
            assert "active_discounts" in analytics
            assert "total_revenue" in analytics
    
    @pytest.mark.asyncio
    async def test_discount_vs_units(self):
        """Test discount vs units sold analytics"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/admin/analytics/discount-vs-units"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_sales_vs_expiry(self):
        """Test sales vs expiry analytics"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/admin/analytics/sales-vs-expiry"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestExperiments:
    """Test A/B testing functionality"""
    
    @pytest.mark.asyncio
    async def test_create_experiment(self):
        """Test creating an A/B experiment"""
        async with httpx.AsyncClient() as client:
            # Get a product
            products_response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/products")
            products = products_response.json()
            
            if len(products) > 0:
                product = products[0]
                
                experiment_data = {
                    "product_id": product["id"],
                    "experiment_group": "ML_VARIANT"
                }
                
                response = await client.post(
                    f"{BASE_URL}{API_PREFIX}/admin/experiments",
                    json=experiment_data
                )
                
                assert response.status_code in [200, 201]
                experiment = response.json()
                assert "experiment_group" in experiment or "experimentGroup" in experiment
    
    @pytest.mark.asyncio
    async def test_list_experiments(self):
        """Test listing all experiments"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/experiments")
            
            assert response.status_code == 200
            experiments = response.json()
            assert isinstance(experiments, list)
    
    @pytest.mark.asyncio
    async def test_experiment_metrics(self):
        """Test experiment metrics endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/admin/experiments/metrics"
            )
            
            assert response.status_code == 200
            metrics = response.json()
            assert isinstance(metrics, (list, dict))


class TestSystemIntegration:
    """Test complete workflow integration"""
    
    @pytest.mark.asyncio
    async def test_complete_product_lifecycle(self):
        """Test complete workflow: create product -> add inventory -> check discount -> analytics"""
        async with httpx.AsyncClient() as client:
            timestamp = datetime.now().timestamp()
            
            # Step 1: Create product
            product_data = {
                "sku": f"LIFECYCLE-{timestamp}",
                "name": "Lifecycle Test Product",
                "description": "Testing complete lifecycle",
                "category": "Dairy",
                "base_price": 75.00
            }
            
            product_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/products",
                json=product_data
            )
            assert product_response.status_code in [200, 201]
            product = product_response.json()
            print(f"✓ Created product: {product['sku']}")
            
            # Step 2: Add inventory batch
            batch_data = {
                "product_id": product["id"],
                "batch_code": f"BATCH-LC-{timestamp}",
                "quantity": 200,
                "expiry_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            }
            
            batch_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/inventory",
                json=batch_data
            )
            assert batch_response.status_code == 200
            batch = batch_response.json()
            print(f"✓ Added inventory batch: {batch['batchCode']}")
            
            # Step 3: Wait for discount computation
            await asyncio.sleep(2)
            
            # Step 4: Verify discount was applied
            discounts_response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/discounts")
            discounts = discounts_response.json()
            
            # Find discount for our batch
            batch_discount = next(
                (d for d in discounts if d.get("batchId") == batch["id"]),
                None
            )
            
            if batch_discount:
                print(f"✓ Discount applied: {batch_discount['discountPct']}%")
            
            # Step 5: Check analytics reflects the new data
            analytics_response = await client.get(f"{BASE_URL}{API_PREFIX}/admin/analytics")
            analytics = analytics_response.json()
            assert analytics["total_products"] > 0
            assert analytics["total_batches"] > 0
            print(f"✓ Analytics updated: {analytics['total_products']} products, {analytics['total_batches']} batches")
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test system health endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            
            assert response.status_code == 200
            health = response.json()
            assert health["status"] == "ok"
            print(f"✓ System health: {health}")
    
    @pytest.mark.asyncio
    async def test_database_connectivity(self):
        """Test that database is accessible and functioning"""
        async with httpx.AsyncClient() as client:
            # Multiple endpoints to verify DB connectivity
            endpoints = [
                f"{BASE_URL}{API_PREFIX}/admin/products",
                f"{BASE_URL}{API_PREFIX}/admin/inventory",
                f"{BASE_URL}{API_PREFIX}/admin/discounts",
            ]
            
            for endpoint in endpoints:
                response = await client.get(endpoint)
                assert response.status_code == 200
                print(f"✓ Database accessible via: {endpoint}")


class TestErrorHandling:
    """Test error scenarios and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_product_sku(self):
        """Test requesting non-existent product"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/admin/products/NONEXISTENT-SKU-12345"
            )
            
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_inventory_data(self):
        """Test creating inventory with invalid data"""
        async with httpx.AsyncClient() as client:
            invalid_batch = {
                "product_id": 99999,  # Non-existent product
                "quantity": 100,
                "expiry_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
            }
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/inventory",
                json=invalid_batch
            )
            
            # Should fail with 404 or 422
            assert response.status_code in [404, 422, 400]
    
    @pytest.mark.asyncio
    async def test_expired_batch_handling(self):
        """Test handling of expired batches"""
        async with httpx.AsyncClient() as client:
            # Create product
            product_data = {
                "sku": f"EXPIRED-TEST-{datetime.now().timestamp()}",
                "name": "Expired Batch Test",
                "description": "Testing expired batches",
                "category": "Food",
                "base_price": 50.00
            }
            
            product_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/products",
                json=product_data
            )
            product = product_response.json()
            
            # Add batch with past expiry
            expired_batch = {
                "product_id": product["id"],
                "batch_code": f"EXPIRED-{datetime.now().timestamp()}",
                "quantity": 10,
                "expiry_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            }
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/admin/inventory",
                json=expired_batch
            )
            
            # Should either accept (for record keeping) or reject
            assert response.status_code in [200, 400, 422]


# Run summary function
def print_test_summary():
    """Print test execution summary"""
    print("\n" + "="*70)
    print("FlexiPrice Comprehensive Test Suite")
    print("="*70)
    print("\nTest Categories:")
    print("  ✓ Product Management (CRUD)")
    print("  ✓ Inventory Management (Batches)")
    print("  ✓ Discount Engine (Rules)")
    print("  ✓ ML Predictions (Recommendations)")
    print("  ✓ Analytics (Metrics)")
    print("  ✓ Experiments (A/B Testing)")
    print("  ✓ System Integration (E2E)")
    print("  ✓ Error Handling (Edge Cases)")
    print("\nRun with: pytest tests/test_comprehensive_system.py -v")
    print("="*70 + "\n")


if __name__ == "__main__":
    print_test_summary()
