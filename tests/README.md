# GenreBend Pro Test Suite

This directory contains tests for GenreBend Pro.

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src

# Run specific test file
python -m pytest tests/test_genrebend_pro.py

# Run with verbose output
python -m pytest tests/ -v
```

## Test Structure

- `test_genrebend_pro.py` - Main test suite
- `conftest.py` - Test configuration and fixtures
- `test_data/` - Test data files (if needed)

## Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Mock Tests**: Test with mocked external APIs
- **End-to-End Tests**: Test complete workflows

## Adding New Tests

1. Create test functions with `test_` prefix
2. Use descriptive test names
3. Include docstrings explaining what's being tested
4. Use appropriate assertions
5. Mock external dependencies

## Test Data

Use mock data for external API calls to ensure tests are:
- Fast
- Reliable
- Independent of external services
- Repeatable
