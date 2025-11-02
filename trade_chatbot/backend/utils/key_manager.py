"""
Alpha Vantage API Key Manager
Handles rotation of multiple API keys to avoid rate limits
"""
import os
import threading
import time
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class AlphaVantageKeyManager:
    """
    Manages multiple Alpha Vantage API keys with rotation to avoid rate limits
    """
    
    def __init__(self, api_keys: List[str]):
        """
        Initialize the key manager with a list of API keys
        
        Args:
            api_keys: List of Alpha Vantage API keys
        """
        self.api_keys = [key.strip() for key in api_keys if key.strip()]
        self.current_key_index = 0
        self.key_usage_count = {key: 0 for key in self.api_keys}
        self.key_last_used = {key: 0.0 for key in self.api_keys}
        self.lock = threading.Lock()
        
        if not self.api_keys:
            raise ValueError("At least one API key must be provided")
        
        logger.info(f"Initialized AlphaVantageKeyManager with {len(self.api_keys)} keys")
    
    def get_current_key(self) -> str:
        """
        Get the currently active API key
        
        Returns:
            Current API key
        """
        with self.lock:
            return self.api_keys[self.current_key_index]
    
    def rotate_key(self) -> str:
        """
        Rotate to the next API key in the list
        
        Returns:
            Next API key
        """
        with self.lock:
            # Move to the next key (circular rotation)
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            new_key = self.api_keys[self.current_key_index]
            
            logger.info(f"Rotated to API key index {self.current_key_index}")
            return new_key
    
    def get_next_key(self) -> str:
        """
        Get the next API key without rotating the current one
        
        Returns:
            Next API key in rotation
        """
        with self.lock:
            next_index = (self.current_key_index + 1) % len(self.api_keys)
            return self.api_keys[next_index]
    
    def mark_key_usage(self, key: str) -> None:
        """
        Mark that a key has been used
        
        Args:
            key: API key that was used
        """
        with self.lock:
            self.key_usage_count[key] = self.key_usage_count.get(key, 0) + 1
            self.key_last_used[key] = time.time()
            
            logger.debug(f"Marked usage for key {key[:5]}... (usage count: {self.key_usage_count[key]})")
    
    def is_rate_limited_response(self, response_data: dict) -> bool:
        """
        Check if the response indicates a rate limit has been hit
        
        Args:
            response_data: Response data from Alpha Vantage API
            
        Returns:
            True if rate limited, False otherwise
        """
        if not response_data:
            return False
            
        # Check for rate limit error messages
        if "Error Message" in response_data:
            error_msg = response_data["Error Message"].lower()
            return (
                "rate limit" in error_msg or 
                "api call frequency" in error_msg or
                "exceeded" in error_msg or
                "limit" in error_msg
            )
            
        if "Information" in response_data:
            info_msg = response_data["Information"].lower()
            return (
                "rate limit" in info_msg or 
                "api call frequency" in info_msg or
                "exceeded" in info_msg or
                "limit" in info_msg
            )
            
        if "Note" in response_data:
            note_msg = response_data["Note"].lower()
            return (
                "rate limit" in note_msg or 
                "api call frequency" in note_msg or
                "exceeded" in note_msg or
                "limit" in note_msg
            )
            
        return False
    
    def get_key_stats(self) -> dict:
        """
        Get statistics about key usage
        
        Returns:
            Dictionary with key usage statistics
        """
        with self.lock:
            return {
                "current_key_index": self.current_key_index,
                "current_key": self.api_keys[self.current_key_index],
                "total_keys": len(self.api_keys),
                "key_usage_count": self.key_usage_count.copy(),
                "key_last_used": self.key_last_used.copy()
            }

# Global instance of the key manager
_key_manager: Optional[AlphaVantageKeyManager] = None

def initialize_key_manager(api_keys: List[str]) -> AlphaVantageKeyManager:
    """
    Initialize the global key manager instance
    
    Args:
        api_keys: List of Alpha Vantage API keys
        
    Returns:
        Initialized key manager instance
    """
    global _key_manager
    _key_manager = AlphaVantageKeyManager(api_keys)
    return _key_manager

def get_key_manager() -> AlphaVantageKeyManager:
    """
    Get the global key manager instance
    
    Returns:
        Key manager instance
    """
    global _key_manager
    if _key_manager is None:
        raise RuntimeError("Key manager not initialized. Call initialize_key_manager first.")
    return _key_manager

def get_current_key() -> str:
    """
    Get the currently active API key
    
    Returns:
        Current API key
    """
    return get_key_manager().get_current_key()

def rotate_key() -> str:
    """
    Rotate to the next API key
    
    Returns:
        Next API key
    """
    return get_key_manager().rotate_key()

def mark_key_usage(key: str) -> None:
    """
    Mark that a key has been used
    
    Args:
        key: API key that was used
    """
    get_key_manager().mark_key_usage(key)

def is_rate_limited_response(response_data: dict) -> bool:
    """
    Check if the response indicates a rate limit has been hit
    
    Args:
        response_data: Response data from Alpha Vantage API
        
    Returns:
        True if rate limited, False otherwise
    """
    return get_key_manager().is_rate_limited_response(response_data)