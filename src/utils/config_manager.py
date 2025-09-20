"""
Configuration management utilities.
"""
import os
import yaml
from loguru import logger
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            self.config = {}
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports nested keys with dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports nested keys with dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def save_config(self, path: str = None):
        """
        Save configuration to file.
        
        Args:
            path: Path to save configuration (uses self.config_path if None)
        """
        save_path = path or self.config_path
        try:
            with open(save_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")


def main():
    """Example usage of the ConfigManager."""
    # Create a sample config file for testing
    sample_config = {
        'project_name': 'Crypto AI Trader',
        'version': '0.1.0',
        'exchanges': ['binance', 'coinbase'],
        'trading_pairs': ['BTC/USDT', 'ETH/USDT']
    }
    
    with open('sample_config.yaml', 'w') as f:
        yaml.dump(sample_config, f)
    
    # Test ConfigManager
    config_manager = ConfigManager('sample_config.yaml')
    print(f"Project name: {config_manager.get('project_name')}")
    print(f"Version: {config_manager.get('version')}")
    print(f"Exchanges: {config_manager.get('exchanges')}")
    print(f"Non-existent key: {config_manager.get('non_existent', 'default_value')}")
    
    # Clean up
    os.remove('sample_config.yaml')


if __name__ == "__main__":
    main()