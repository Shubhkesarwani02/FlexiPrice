"""
Test Batch Processing and Scale

Tests for large-scale batch discount recomputation with 1000+ batches.
Validates performance and correctness of parallel processing.
"""

import pytest
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List

from prisma import Prisma
from app.core.discount_engine import get_discount_engine
from app.services.batch_discount_service import BatchDiscountService
from app.tasks import recompute_all_discounts, parallel_recompute_discounts


@pytest.fixture
async def db():
    """Create database connection."""
    db = Prisma()
    await db.connect()
    yield db
    await db.disconnect()


@pytest.fixture
async def cleanup_test_data(db):
    """Cleanup test data after tests."""
    yield
    # Clean up test products and batches
    await db.batchdiscount.delete_many(where={})
    await db.inventorybatch.delete_many(where={})
    await db.product.delete_many(where={"sku": {"startswith": "TEST-"}})


@pytest.mark.asyncio
async def test_create_1000_batches(db, cleanup_test_data):
    """
    Test creation of 1000 synthetic batches for load testing.
    """
    print("\n=== Creating 1000 synthetic batches ===")
    
    # Create test products
    num_products = 50
    products = []
    
    for i in range(num_products):
        product = await db.product.create(
            data={
                "sku": f"TEST-PROD-{i:04d}",
                "name": f"Test Product {i}",
                "category": f"Category{i % 5}",
                "basePrice": Decimal(str(10.00 + i * 2)),
                "description": f"Test product for batch processing"
            }
        )
        products.append(product)
    
    print(f"Created {len(products)} test products")
    
    # Create 1000 batches across products
    num_batches = 1000
    batches = []
    
    for i in range(num_batches):
        product = products[i % num_products]
        days_until_expiry = 5 + (i % 25)  # Vary expiry from 5 to 30 days
        
        batch = await db.inventorybatch.create(
            data={
                "productId": product.id,
                "batchCode": f"BATCH-{i:04d}",
                "quantity": 10 + (i % 90),  # Vary quantity 10-100
                "expiryDate": datetime.now() + timedelta(days=days_until_expiry)
            }
        )
        batches.append(batch)
    
    print(f"Created {len(batches)} test batches")
    
    # Verify creation
    count = await db.inventorybatch.count()
    assert count >= num_batches, f"Expected at least {num_batches} batches, got {count}"
    
    return products, batches


@pytest.mark.asyncio
async def test_recompute_1000_batches_sequential(db, cleanup_test_data):
    """
    Test sequential batch discount recomputation with 1000 batches.
    Measures performance and validates results.
    """
    print("\n=== Testing Sequential Recomputation ===")
    
    # Create test data
    products, batches = await test_create_1000_batches(db, cleanup_test_data)
    
    # Run recomputation
    import time
    start_time = time.time()
    
    result = recompute_all_discounts(days_threshold=35, chunk_size=100)
    
    elapsed = time.time() - start_time
    
    print(f"\nRecomputation Results:")
    print(f"  Total processed: {result['total_processed']}")
    print(f"  Discounts written: {result['discounts_written']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Chunks processed: {result['chunks_processed']}")
    print(f"  Time elapsed: {elapsed:.2f} seconds")
    print(f"  Batches per second: {result['total_processed']/elapsed:.2f}")
    
    # Validate results
    assert result['total_processed'] == len(batches), "Not all batches were processed"
    assert result['errors'] == 0, "Errors occurred during processing"
    assert result['discounts_written'] > 0, "No discounts were written"
    
    # Verify discounts were created
    discount_count = await db.batchdiscount.count()
    print(f"  Total discounts in DB: {discount_count}")
    assert discount_count == len(batches), "Discount count mismatch"
    
    # Verify a sample discount
    sample_batch = batches[0]
    discount = await db.batchdiscount.find_first(
        where={"batchId": sample_batch.id}
    )
    
    assert discount is not None, "Sample discount not found"
    assert discount.computedPrice > 0, "Computed price is invalid"
    assert discount.discountPct >= 0, "Discount percentage is invalid"
    print(f"  Sample discount: {discount.discountPct*100:.1f}% off, price: ${discount.computedPrice}")


@pytest.mark.asyncio
async def test_storefront_price_computation(db, cleanup_test_data):
    """
    Test storefront price computation with multiple batches per product.
    """
    print("\n=== Testing Storefront Price Computation ===")
    
    # Create a product
    product = await db.product.create(
        data={
            "sku": "TEST-STOREFRONT-001",
            "name": "Test Storefront Product",
            "category": "TestCategory",
            "basePrice": Decimal("100.00")
        }
    )
    
    # Create multiple batches with different expiry dates
    batch1 = await db.inventorybatch.create(
        data={
            "productId": product.id,
            "batchCode": "BATCH-EXPIRE-SOON",
            "quantity": 50,
            "expiryDate": datetime.now() + timedelta(days=5)
        }
    )
    
    batch2 = await db.inventorybatch.create(
        data={
            "productId": product.id,
            "batchCode": "BATCH-EXPIRE-LATER",
            "quantity": 100,
            "expiryDate": datetime.now() + timedelta(days=20)
        }
    )
    
    # Compute discounts
    engine = get_discount_engine()
    
    price1, disc1, _ = engine.compute_batch_price(
        base_price=product.basePrice,
        expiry_date=(datetime.now() + timedelta(days=5)).date(),
        quantity=50,
        category=product.category
    )
    
    price2, disc2, _ = engine.compute_batch_price(
        base_price=product.basePrice,
        expiry_date=(datetime.now() + timedelta(days=20)).date(),
        quantity=100,
        category=product.category
    )
    
    # Create discounts
    await db.batchdiscount.create(
        data={
            "batchId": batch1.id,
            "computedPrice": price1,
            "discountPct": disc1,
            "expiresAt": batch1.expiryDate
        }
    )
    
    await db.batchdiscount.create(
        data={
            "batchId": batch2.id,
            "computedPrice": price2,
            "discountPct": disc2,
            "expiresAt": batch2.expiryDate
        }
    )
    
    # Get storefront price
    prices = await BatchDiscountService.get_storefront_prices([product.id])
    
    storefront_price, discount_pct = prices[product.id]
    
    print(f"\nProduct base price: ${product.basePrice}")
    print(f"Batch 1 (expires soon): ${price1} ({disc1*100:.1f}% off)")
    print(f"Batch 2 (expires later): ${price2} ({disc2*100:.1f}% off)")
    print(f"Storefront price: ${storefront_price} ({discount_pct*100:.1f}% off)")
    
    # Storefront price should be the minimum
    expected_min = min(price1, price2)
    assert storefront_price == expected_min, f"Expected {expected_min}, got {storefront_price}"
    assert storefront_price < product.basePrice, "Storefront price should be less than base price"


@pytest.mark.asyncio
async def test_batch_chunking(db, cleanup_test_data):
    """
    Test that batch processing correctly chunks data.
    """
    print("\n=== Testing Batch Chunking ===")
    
    # Create test data
    products, batches = await test_create_1000_batches(db, cleanup_test_data)
    
    # Test with different chunk sizes
    chunk_sizes = [50, 100, 200]
    
    for chunk_size in chunk_sizes:
        print(f"\nTesting with chunk_size={chunk_size}")
        
        # Clear existing discounts
        await db.batchdiscount.delete_many(where={})
        
        result = recompute_all_discounts(days_threshold=35, chunk_size=chunk_size)
        
        expected_chunks = (len(batches) + chunk_size - 1) // chunk_size
        
        print(f"  Expected chunks: {expected_chunks}")
        print(f"  Actual chunks: {result['chunks_processed']}")
        print(f"  Batches processed: {result['total_processed']}")
        
        assert result['chunks_processed'] == expected_chunks, "Chunk count mismatch"
        assert result['total_processed'] == len(batches), "Not all batches processed"


@pytest.mark.asyncio
async def test_discount_update_vs_create(db, cleanup_test_data):
    """
    Test that existing discounts are updated, not duplicated.
    """
    print("\n=== Testing Discount Update vs Create ===")
    
    # Create a simple test case
    product = await db.product.create(
        data={
            "sku": "TEST-UPDATE-001",
            "name": "Test Update Product",
            "category": "TestCategory",
            "basePrice": Decimal("50.00")
        }
    )
    
    batch = await db.inventorybatch.create(
        data={
            "productId": product.id,
            "batchCode": "BATCH-UPDATE-TEST",
            "quantity": 50,
            "expiryDate": datetime.now() + timedelta(days=10)
        }
    )
    
    # Run recompute first time
    result1 = recompute_all_discounts(days_threshold=15, chunk_size=10)
    discount_count_1 = await db.batchdiscount.count(where={"batchId": batch.id})
    
    print(f"\nFirst run:")
    print(f"  Discounts written: {result1['discounts_written']}")
    print(f"  Discount count for batch: {discount_count_1}")
    
    # Run recompute second time (should update, not create new)
    result2 = recompute_all_discounts(days_threshold=15, chunk_size=10)
    discount_count_2 = await db.batchdiscount.count(where={"batchId": batch.id})
    
    print(f"\nSecond run:")
    print(f"  Discounts written: {result2['discounts_written']}")
    print(f"  Discount count for batch: {discount_count_2}")
    
    assert discount_count_1 == 1, "Should create exactly 1 discount"
    assert discount_count_2 == 1, "Should still have exactly 1 discount (updated, not duplicated)"


@pytest.mark.asyncio
async def test_performance_metrics(db, cleanup_test_data):
    """
    Test and report performance metrics for batch processing.
    """
    print("\n=== Performance Metrics Test ===")
    
    products, batches = await test_create_1000_batches(db, cleanup_test_data)
    
    import time
    
    # Test different configurations
    configs = [
        {"chunk_size": 50, "desc": "Small chunks"},
        {"chunk_size": 100, "desc": "Medium chunks"},
        {"chunk_size": 250, "desc": "Large chunks"},
    ]
    
    results = []
    
    for config in configs:
        # Clear discounts
        await db.batchdiscount.delete_many(where={})
        
        start = time.time()
        result = recompute_all_discounts(
            days_threshold=35,
            chunk_size=config["chunk_size"]
        )
        elapsed = time.time() - start
        
        results.append({
            "config": config["desc"],
            "chunk_size": config["chunk_size"],
            "elapsed": elapsed,
            "batches_per_sec": result['total_processed'] / elapsed,
            "chunks": result['chunks_processed']
        })
    
    print("\nPerformance Results:")
    print(f"{'Configuration':<20} {'Chunk Size':<12} {'Time (s)':<10} {'Batches/s':<12} {'Chunks':<8}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['config']:<20} {r['chunk_size']:<12} {r['elapsed']:<10.2f} {r['batches_per_sec']:<12.1f} {r['chunks']:<8}")
    
    # All should complete successfully
    for r in results:
        assert r['batches_per_sec'] > 0, "Processing rate should be positive"


if __name__ == "__main__":
    """
    Run tests directly for debugging.
    """
    import sys
    sys.path.insert(0, "/Users/shubh/Desktop/FlexiPrice/backend")
    
    asyncio.run(test_create_1000_batches(None, None))
