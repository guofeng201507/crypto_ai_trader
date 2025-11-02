"""
Integration test to verify that the Alpha Vantage key rotation system works with actual API keys.
This test will verify that the system can handle multiple API keys properly.
"""
import os
import sys
import pytest

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from utils.key_manager import (
    initialize_key_manager,
    get_current_key,
    rotate_key,
    get_key_manager
)

def test_key_rotation_integration():
    """Test key rotation with actual API keys from environment variables"""
    # Get API keys from environment variables
    api_keys_env = os.environ.get('ALPHA_VANTAGE_API_KEYS', 'TEST_KEY1,TEST_KEY2,TEST_KEY3')
    api_keys = [key.strip() for key in api_keys_env.split(',') if key.strip()]
    
    # Initialize the key manager
    initialize_key_manager(api_keys)
    
    # Test initial key
    current_key = get_current_key()
    assert current_key in api_keys
    
    # Test key rotation
    rotated_keys = []
    for i in range(len(api_keys) * 2):  # Rotate twice through all keys
        new_key = rotate_key()
        rotated_keys.append(new_key)
        assert new_key in api_keys
    
    # Test key stats
    manager = get_key_manager()
    stats = manager.get_key_stats()
    assert stats['total_keys'] == len(api_keys)
    assert stats['current_key'] in api_keys

if __name__ == "__main__":
    # Run the test
    test_key_rotation_integration()
    print("Integration test completed successfully!")