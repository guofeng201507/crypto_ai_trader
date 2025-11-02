"""
Test script for Alpha Vantage API key rotation system
"""
import sys
import os
import pytest

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.key_manager import (
    AlphaVantageKeyManager,
    initialize_key_manager,
    get_key_manager,
    get_current_key,
    rotate_key,
    is_rate_limited_response
)

def test_key_rotation():
    """Test the key rotation functionality"""
    # Initialize with test keys
    test_keys = ["KEY1", "KEY2", "KEY3", "KEY4"]
    initialize_key_manager(test_keys)
    
    # Test getting current key
    current = get_current_key()
    assert current == "KEY1"
    
    # Test rotating keys
    next_key = rotate_key()
    assert next_key == "KEY2"
    
    next_key = rotate_key()
    assert next_key == "KEY3"
    
    # Test circular rotation
    rotate_key()  # KEY4
    next_key = rotate_key()  # Back to KEY1
    assert next_key == "KEY1"

def test_rate_limit_detection():
    """Test rate limit detection functionality"""
    # Test case 1: Normal response
    normal_response = {"Global Quote": {"01. symbol": "AAPL", "05. price": "150.00"}}
    is_limited = is_rate_limited_response(normal_response)
    assert is_limited == False
    
    # Test case 2: Rate limit response
    rate_limit_response = {"Error Message": "API call frequency limit reached"}
    is_limited = is_rate_limited_response(rate_limit_response)
    assert is_limited == True
    
    # Test case 3: Info message rate limit
    info_limit_response = {"Information": "Thank you for using Alpha Vantage!"}
    is_limited = is_rate_limited_response(info_limit_response)
    # This should not be detected as a rate limit
    assert is_limited == False
    
    # Test case 4: Actual rate limit message in Information field
    actual_rate_limit_response = {"Information": "Please consider optimizing your API call frequency to avoid rate limiting."}
    is_limited = is_rate_limited_response(actual_rate_limit_response)
    assert is_limited == True

def test_key_manager_initialization():
    """Test key manager initialization"""
    # Initialize with test keys
    test_keys = ["TEST_KEY1", "TEST_KEY2"]
    manager = AlphaVantageKeyManager(test_keys)
    
    # Test that keys are properly stored
    assert len(manager.api_keys) == 2
    assert "TEST_KEY1" in manager.api_keys
    assert "TEST_KEY2" in manager.api_keys
    
    # Test current key
    assert manager.get_current_key() == "TEST_KEY1"
    
    # Test key stats
    stats = manager.get_key_stats()
    assert "current_key_index" in stats
    assert "current_key" in stats
    assert "total_keys" in stats

def test_empty_key_list():
    """Test that empty key list raises an error"""
    with pytest.raises(ValueError):
        AlphaVantageKeyManager([])

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])