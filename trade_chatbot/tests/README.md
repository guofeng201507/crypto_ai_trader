# Trade Chatbot Tests

This directory contains unit tests and integration tests for the trade chatbot application.

## Test Structure

```
tests/
├── test_natural_language_processing.py  # Tests for natural language query interpretation
├── test_mcp_wrapper.py                   # Tests for Alpha Vantage MCP wrapper
├── conftest.py                           # pytest configuration
└── __init__.py                          # Package initialization
```

## Running Tests

To run all tests:

```bash
cd trade_chatbot
pytest tests/
```

To run tests with verbose output:

```bash
cd trade_chatbot
pytest tests/ -v
```

To run specific test files:

```bash
cd trade_chatbot
pytest tests/test_natural_language_processing.py
pytest tests/test_mcp_wrapper.py
```

To run tests with coverage:

```bash
cd trade_chatbot
pytest tests/ --cov=backend --cov-report=html
```

## Test Categories

### Natural Language Processing Tests
- `test_natural_language_processing.py`: Tests for interpreting user queries in natural language
- Verifies that queries like "What is the price of Apple stock?" are correctly mapped to MCP methods

### MCP Wrapper Tests
- `test_mcp_wrapper.py`: Tests for the Alpha Vantage MCP wrapper implementation
- Verifies JSON-RPC 2.0 compliance and correct method routing

## Adding New Tests

1. Create a new test file following the naming convention `test_*.py`
2. Use pytest markers to categorize tests:
   - `@pytest.mark.unit` for unit tests
   - `@pytest.mark.integration` for integration tests
   - `@pytest.mark.mcp` for MCP-related tests
3. Follow the existing test structure and naming conventions
4. Use mocks for external dependencies to ensure tests are isolated

## Test Dependencies

Make sure to install test dependencies:

```bash
pip install pytest pytest-cov pytest-mock
```