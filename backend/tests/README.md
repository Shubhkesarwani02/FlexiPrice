# Tests directory for FlexiPrice backend

This directory contains unit and integration tests for the FlexiPrice API.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_discount_engine.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_discount_engine.py` - Unit tests for discount computation logic
- `test_api_*.py` - API endpoint integration tests (to be added)
- `test_services_*.py` - Service layer tests (to be added)
