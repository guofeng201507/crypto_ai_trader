## 14. Coding Agent Instructions

### 14.1 Working with API Key Rotation Systems

When working with systems that implement API key rotation (like the Alpha Vantage key rotation system), follow these guidelines:

1. **Understand the Key Manager Pattern**: The system uses a `key_manager.py` module that handles multiple API keys with automatic rotation when rate limits are hit.

2. **Use the Provided Utilities**: Instead of directly accessing API keys, use the provided utility functions:
   ```python
   from utils.key_manager import get_current_key, rotate_key, mark_key_usage
   
   # Get current API key
   api_key = get_current_key()
   
   # Mark key usage after successful API call
   mark_key_usage(api_key)
   
   # Rotate to next key when rate limit is hit
   new_key = rotate_key()
   ```

3. **Implement Retry Logic**: When making API calls, implement retry logic that rotates keys:
   ```python
   def call_api_with_retry(function, max_retries=3, **params):
       for attempt in range(max_retries):
           api_key = get_current_key()
           # Make API call
           response = make_api_call(function, api_key=api_key, **params)
           
           if is_rate_limited(response):
               # Rotate to next key and retry
               rotate_key()
               continue
           else:
               # Success - mark key usage and return
               mark_key_usage(api_key)
               return response
       return None
   ```

4. **Test Key Rotation**: The system includes comprehensive tests for key rotation in `tests/test_key_rotation.py`. When adding new features that use API keys, ensure they work with the key rotation system by running these tests.

5. **Environment Configuration**: Configure multiple API keys using the `ALPHA_VANTAGE_API_KEYS` environment variable as a comma-separated list:
   ```
   ALPHA_VANTAGE_API_KEYS=key1,key2,key3
   ```

### 14.2 Testing Guidelines

1. **Regression Testing**: The system includes regression tests in the `tests/` directory. Run all tests before submitting changes:
   ```bash
   cd trade_chatbot
   pytest tests/
   ```

2. **New Feature Testing**: When adding new features, create corresponding tests following the existing patterns in the `tests/` directory.

3. **Key Rotation Testing**: Test the key rotation functionality specifically with:
   ```bash
   cd trade_chatbot
   pytest tests/test_key_rotation.py
   ```

4. **Coverage**: Ensure new code has adequate test coverage by running tests with coverage:
   ```bash
   cd trade_chatbot
   pytest tests/ --cov=backend --cov-report=term-missing
   ```

---

> Version: 1.0 — This document represents best practices from top quantitative trading firms and should be customized based on your specific requirements and compliance needs.