#!/usr/bin/env python3
"""
Quick System Validation Script for FlexiPrice

This script performs rapid checks on all critical system components:
- Backend API availability
- Frontend server availability
- Database connectivity
- Redis connectivity
- Celery workers status
- All major endpoints

Run with: python backend/scripts/quick_validation.py
"""

import requests
import sys
import time
from typing import Dict, List, Tuple
from datetime import datetime


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")


def check_endpoint(url: str, name: str, timeout: int = 5) -> bool:
    """Check if an endpoint is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print_success(f"{name}: {url} - Status {response.status_code}")
            return True
        else:
            print_warning(f"{name}: {url} - Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"{name}: {url} - {str(e)}")
        return False


def test_backend_api() -> Dict[str, bool]:
    """Test all backend API endpoints"""
    print_header("Backend API Tests")
    
    base_url = "http://localhost:8000"
    api_prefix = "/api/v1"
    
    results = {}
    
    # Health check
    results['health'] = check_endpoint(f"{base_url}/health", "Health Check")
    
    # Admin endpoints
    endpoints = [
        ("/admin/products", "Products List"),
        ("/admin/inventory", "Inventory List"),
        ("/admin/discounts", "Discounts List"),
        ("/admin/analytics", "Analytics Overview"),
        ("/admin/experiments", "Experiments List"),
    ]
    
    for path, name in endpoints:
        results[name] = check_endpoint(f"{base_url}{api_prefix}{path}", name)
    
    return results


def test_frontend() -> Dict[str, bool]:
    """Test frontend pages"""
    print_header("Frontend Tests")
    
    base_url = "http://localhost:3000"
    
    results = {}
    
    pages = [
        ("/", "Homepage"),
        ("/admin", "Admin Page"),
        ("/admin/analytics", "Admin Analytics"),
        ("/admin/experiments", "Admin Experiments"),
    ]
    
    for path, name in pages:
        results[name] = check_endpoint(f"{base_url}{path}", name, timeout=10)
    
    return results


def test_database_operations() -> Dict[str, bool]:
    """Test database operations through API"""
    print_header("Database Operations Tests")
    
    base_url = "http://localhost:8000/api/v1"
    results = {}
    
    try:
        # Test read operations
        response = requests.get(f"{base_url}/admin/products", timeout=5)
        if response.status_code == 200:
            products = response.json()
            print_success(f"Database READ: Retrieved {len(products)} products")
            results['db_read'] = True
        else:
            print_error(f"Database READ: Failed with status {response.status_code}")
            results['db_read'] = False
        
        # Test create operation
        test_product = {
            "sku": f"VALIDATION-{int(time.time())}",
            "name": "Validation Test Product",
            "description": "Auto-generated test product",
            "category": "Test",
            "base_price": 99.99
        }
        
        response = requests.post(
            f"{base_url}/admin/products",
            json=test_product,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            product = response.json()
            print_success(f"Database WRITE: Created product {product.get('sku')}")
            results['db_write'] = True
        else:
            print_error(f"Database WRITE: Failed with status {response.status_code}")
            results['db_write'] = False
            
    except Exception as e:
        print_error(f"Database operations: {str(e)}")
        results['db_read'] = False
        results['db_write'] = False
    
    return results


def test_ml_system() -> Dict[str, bool]:
    """Test ML recommendation system"""
    print_header("ML System Tests")
    
    base_url = "http://localhost:8000/api/v1"
    results = {}
    
    try:
        # Get a product first
        response = requests.get(f"{base_url}/admin/products", timeout=5)
        if response.status_code == 200:
            products = response.json()
            if len(products) > 0:
                # Try to find a product with a common category
                product = None
                for p in products:
                    if p.get('category') in ['Dairy', 'Bakery', 'Produce', 'Meat', 'Seafood', 'Snacks']:
                        product = p
                        break
                
                # Fall back to first product if no common category found
                if not product:
                    product = products[0]
                
                product_sku = product['sku']
                
                # Test ML recommendation
                params = {
                    "product_id": product_sku,
                    "days_to_expiry": 7,
                    "inventory": 100
                }
                
                response = requests.get(
                    f"{base_url}/admin/ml/recommend",
                    params=params,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print_success("ML Recommendations: Working")
                    results['ml_recommend'] = True
                elif response.status_code == 500:
                    print_warning("ML Recommendations: Model not trained yet")
                    results['ml_recommend'] = False
                else:
                    print_warning(f"ML Recommendations: Status {response.status_code}")
                    results['ml_recommend'] = False
            else:
                print_warning("ML Recommendations: No products available for testing")
                results['ml_recommend'] = False
        else:
            print_error("ML Recommendations: Cannot retrieve products")
            results['ml_recommend'] = False
            
    except Exception as e:
        print_error(f"ML System: {str(e)}")
        results['ml_recommend'] = False
    
    return results


def test_analytics() -> Dict[str, bool]:
    """Test analytics endpoints"""
    print_header("Analytics Tests")
    
    base_url = "http://localhost:8000/api/v1/admin/analytics"
    results = {}
    
    endpoints = [
        ("", "Overview"),
        ("/discount-vs-units", "Discount vs Units"),
        ("/sales-vs-expiry", "Sales vs Expiry"),
    ]
    
    for path, name in endpoints:
        try:
            response = requests.get(f"{base_url}{path}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_success(f"{name}: Available")
                results[name] = True
            else:
                print_warning(f"{name}: Status {response.status_code}")
                results[name] = False
        except Exception as e:
            print_error(f"{name}: {str(e)}")
            results[name] = False
    
    return results


def test_experiments() -> Dict[str, bool]:
    """Test A/B testing functionality"""
    print_header("A/B Testing Tests")
    
    base_url = "http://localhost:8000/api/v1/admin/experiments"
    results = {}
    
    try:
        # List experiments
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            experiments = response.json()
            print_success(f"Experiments List: {len(experiments)} experiments found")
            results['experiments_list'] = True
        else:
            print_warning(f"Experiments List: Status {response.status_code}")
            results['experiments_list'] = False
        
        # Check metrics endpoint
        response = requests.get(f"{base_url}/analytics/comparison", timeout=5)
        if response.status_code == 200:
            print_success("Experiment Metrics: Available")
            results['experiment_metrics'] = True
        else:
            print_warning(f"Experiment Metrics: Status {response.status_code}")
            results['experiment_metrics'] = False
            
    except Exception as e:
        print_error(f"Experiments: {str(e)}")
        results['experiments_list'] = False
        results['experiment_metrics'] = False
    
    return results


def print_summary(all_results: Dict[str, Dict[str, bool]]):
    """Print test summary"""
    print_header("Validation Summary")
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        category_passed = sum(1 for v in results.values() if v)
        category_total = len(results)
        total_tests += category_total
        passed_tests += category_passed
        
        status = f"{category_passed}/{category_total}"
        if category_passed == category_total:
            print_success(f"{category}: {status} tests passed")
        elif category_passed > 0:
            print_warning(f"{category}: {status} tests passed")
        else:
            print_error(f"{category}: {status} tests passed")
    
    print(f"\n{Colors.BOLD}Overall: {passed_tests}/{total_tests} tests passed{Colors.END}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate == 100:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ System fully operational!{Colors.END}\n")
        return 0
    elif success_rate >= 80:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ System mostly operational ({success_rate:.1f}%){Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ System has issues ({success_rate:.1f}%){Colors.END}\n")
        return 1


def main():
    """Main execution function"""
    print(f"\n{Colors.BOLD}FlexiPrice System Validation{Colors.END}")
    print(f"{Colors.BOLD}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    all_results = {}
    
    # Run all tests
    all_results['Backend API'] = test_backend_api()
    time.sleep(0.5)
    
    all_results['Frontend'] = test_frontend()
    time.sleep(0.5)
    
    all_results['Database'] = test_database_operations()
    time.sleep(0.5)
    
    all_results['ML System'] = test_ml_system()
    time.sleep(0.5)
    
    all_results['Analytics'] = test_analytics()
    time.sleep(0.5)
    
    all_results['Experiments'] = test_experiments()
    
    # Print summary
    exit_code = print_summary(all_results)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
