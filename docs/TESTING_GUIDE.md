# Tunnelgrid.ai Testing Guide

## 🧪 Testing Overview

This document provides a comprehensive guide to testing the Tunnelgrid.ai platform, including how to run tests, write new tests, and understand the testing strategy.

## 📁 Test Organization

The tests are organized into different categories in the `tests/` directory:

```
tests/
├── backend/          # Backend-specific tests
├── frontend/         # Frontend-specific tests  
├── integration/      # Full-stack integration tests
├── api/              # API endpoint tests
├── unit/             # Unit tests
└── data/             # Test data and fixtures
```

## 🏃‍♂️ Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --backend
python run_tests.py --frontend
python run_tests.py --integration

# Run with coverage report
python run_tests.py --coverage
```

### Advanced Test Running

```bash
# Run a specific test file
pytest tests/backend/test_brands.py -v

# Run a specific test function
pytest tests/backend/test_brands.py::test_search_brands -v

# Run tests with specific markers
pytest -m "not slow" tests/

# Run tests and stop on first failure
pytest tests/ -x

# Run tests with detailed output
pytest tests/ -v --tb=long
```

## 🧩 Test Categories

### 1. Backend Tests (`tests/backend/`)

Tests for Python backend functionality:

- **API Logic**: Test business logic in route handlers
- **Data Models**: Test Pydantic models and validation
- **External Integrations**: Test Logo.dev, GroqCloud, Supabase integrations
- **Error Handling**: Test error scenarios and exception handling

**Example Backend Test:**
```python
def test_brand_search():
    """Test brand search functionality"""
    # Test implementation
    result = search_brand("Apple")
    assert result["status"] == "success"
    assert "name" in result["data"]
```

### 2. Frontend Tests (`tests/frontend/`)

Tests for React frontend functionality:

- **Component Rendering**: Test that components render correctly
- **User Interactions**: Test button clicks, form submissions, etc.
- **State Management**: Test React hooks and context
- **API Integration**: Test frontend services that call backend

### 3. Integration Tests (`tests/integration/`)

End-to-end tests that verify the entire system:

- **Complete Workflows**: Test full user journeys
- **Frontend-Backend Communication**: Test API calls and responses
- **Database Operations**: Test data persistence and retrieval
- **External Service Integration**: Test with real external APIs

### 4. API Tests (`tests/api/`)

Direct tests of API endpoints:

- **HTTP Status Codes**: Verify correct response codes
- **Request/Response Format**: Test JSON structure
- **Authentication**: Test API security
- **Rate Limiting**: Test API limits

**Example API Test:**
```python
async def test_brands_search_endpoint():
    """Test the brands search API endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/brands/search?q=apple")
        assert response.status_code == 200
        assert "brands" in response.json()
```

### 5. Unit Tests (`tests/unit/`)

Isolated tests of individual functions:

- **Pure Functions**: Test functions without side effects
- **Utility Functions**: Test helper functions
- **Data Transformations**: Test data processing logic
- **Validation Logic**: Test input validation

## 🔧 Test Configuration

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -ra
    --strict-markers
    --tb=short
asyncio_mode = auto

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
```

### Test Markers

Use markers to categorize tests:

```python
import pytest

@pytest.mark.slow
def test_large_dataset_processing():
    """This test takes a long time"""
    pass

@pytest.mark.integration
def test_full_workflow():
    """This test requires the full system"""
    pass

@pytest.mark.api
def test_api_endpoint():
    """This test calls API endpoints"""
    pass
```

## ✍️ Writing Tests

### Test Naming Conventions

- **Test files**: `test_*.py`
- **Test functions**: `test_*`
- **Test classes**: `Test*`

### Good Test Structure

Follow the **Arrange, Act, Assert** pattern:

```python
def test_persona_generation():
    # Arrange - Set up test data
    brand_data = {"name": "Apple", "industry": "Technology"}
    
    # Act - Execute the function being tested
    personas = generate_personas(brand_data)
    
    # Assert - Verify the results
    assert len(personas) > 0
    assert all("name" in persona for persona in personas)
    assert all("description" in persona for persona in personas)
```

### Async Test Example

```python
import pytest

@pytest.mark.asyncio
async def test_async_brand_analysis():
    """Test asynchronous brand analysis"""
    result = await analyze_brand_async("Apple")
    assert result["status"] == "completed"
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@patch('app.services.groq_client.generate_personas')
def test_persona_generation_with_mock(mock_groq):
    """Test persona generation with mocked AI service"""
    # Arrange
    mock_groq.return_value = [{"name": "Tech Enthusiast"}]
    
    # Act
    result = generate_personas({"name": "Apple"})
    
    # Assert
    assert len(result) == 1
    assert result[0]["name"] == "Tech Enthusiast"
    mock_groq.assert_called_once()
```

## 🎯 Test Coverage

### Generating Coverage Reports

```bash
# Generate HTML coverage report
python run_tests.py --coverage

# View the report
# Open htmlcov/index.html in your browser
```

### Coverage Goals

- **Backend Code**: Aim for 80%+ coverage
- **Critical Functions**: 100% coverage for core business logic
- **API Endpoints**: 100% coverage for all endpoints
- **Error Handling**: Test all error scenarios

### Reading Coverage Reports

- **Green**: Lines covered by tests
- **Red**: Lines not covered by tests
- **Yellow**: Partially covered lines (e.g., branches)

## 🔍 Testing Best Practices

### 1. Test Independence

Each test should be independent and not rely on other tests:

```python
def test_create_brand():
    """Each test should clean up after itself"""
    # Create test data
    brand = create_brand("Test Brand")
    
    # Test logic
    assert brand.name == "Test Brand"
    
    # Cleanup (if needed)
    delete_brand(brand.id)
```

### 2. Use Fixtures for Common Setup

```python
import pytest

@pytest.fixture
def sample_brand():
    """Fixture providing a sample brand for tests"""
    return {
        "name": "Apple",
        "industry": "Technology",
        "description": "Consumer electronics company"
    }

def test_brand_analysis(sample_brand):
    """Test using the fixture"""
    result = analyze_brand(sample_brand)
    assert result["success"] is True
```

### 3. Test Edge Cases

```python
def test_brand_search_edge_cases():
    """Test edge cases for brand search"""
    # Empty query
    assert search_brand("") == {"brands": []}
    
    # Very long query
    long_query = "a" * 1000
    result = search_brand(long_query)
    assert "error" in result
    
    # Special characters
    assert search_brand("@#$%") == {"brands": []}
```

### 4. Test Error Conditions

```python
def test_api_key_missing():
    """Test behavior when API key is missing"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ConfigurationError):
            initialize_groq_client()
```

## 🚨 Debugging Failed Tests

### Common Debugging Techniques

1. **Add Print Statements**: Use `print()` to debug test data
2. **Use pytest --pdb**: Drop into debugger on failure
3. **Check Logs**: Look at application logs during test runs
4. **Isolate Tests**: Run single tests to isolate issues

### Example Debugging Session

```bash
# Run with debugger
pytest tests/backend/test_brands.py::test_failing_function --pdb

# Run with verbose output
pytest tests/backend/test_brands.py -v -s

# Run specific test with detailed tracebacks
pytest tests/backend/test_brands.py::test_failing_function --tb=long
```

## 🔄 Continuous Integration

### Pre-commit Testing

Before committing code, always run:

```bash
# Run all tests
python run_tests.py

# Run linting (if configured)
flake8 backend/
npm run lint  # for frontend

# Run type checking
mypy backend/app/
```

### CI/CD Pipeline Testing

In CI/CD environments, tests should:

1. Run on every commit
2. Test multiple Python/Node versions
3. Generate coverage reports
4. Fail builds on test failures

## 📊 Test Data Management

### Test Database

- Use separate test database
- Reset data between test runs
- Use fixtures for consistent test data

### Mock Data

```python
# tests/data/mock_data.py
SAMPLE_BRANDS = [
    {"name": "Apple", "industry": "Technology"},
    {"name": "Nike", "industry": "Sports"},
    {"name": "Coca-Cola", "industry": "Beverages"}
]

SAMPLE_PERSONAS = [
    {"name": "Tech Enthusiast", "age_range": "25-35"},
    {"name": "Casual User", "age_range": "18-45"}
]
```

## 🎭 Performance Testing

### Load Testing (Future Enhancement)

```python
@pytest.mark.slow
def test_concurrent_requests():
    """Test system under load"""
    # Simulate multiple concurrent requests
    import asyncio
    
    async def make_request():
        # Make API request
        pass
    
    # Run 100 concurrent requests
    await asyncio.gather(*[make_request() for _ in range(100)])
```

## 📝 Test Documentation

### Documenting Test Cases

```python
def test_brand_persona_generation():
    """
    Test Case: Brand Persona Generation
    
    Given: A valid brand with complete information
    When: Requesting persona generation
    Then: Should return 3-5 distinct personas with required fields
    
    Requirements Tested:
    - REQ-001: Persona generation functionality
    - REQ-002: Persona data validation
    """
    # Test implementation
```

This comprehensive testing guide should help maintain high code quality and catch issues early in the development process! 