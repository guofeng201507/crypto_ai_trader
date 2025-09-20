"""
Unit tests for the ConfigManager class
"""
import unittest
import os
import tempfile
import yaml
from src.utils.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary config file for testing
        self.test_config = {
            'exchanges': [
                {'name': 'binance', 'enabled': True},
                {'name': 'okx', 'enabled': True}
            ],
            'trading_pairs': ['SOL/USDT', 'DOT/USDT'],
            'refresh_rate': 5,
            'threshold_percentage': 0.5,
            'log_level': 'INFO',
            'log_file': 'test.log'
        }
        
        # Create a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_config, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Clean up the temporary file
        os.unlink(self.temp_file.name)
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file"""
        config_manager = ConfigManager(self.temp_file.name)
        config = config_manager.get_config()
        
        self.assertEqual(config['exchanges'], self.test_config['exchanges'])
        self.assertEqual(config['trading_pairs'], self.test_config['trading_pairs'])
        self.assertEqual(config['refresh_rate'], self.test_config['refresh_rate'])
        self.assertEqual(config['threshold_percentage'], self.test_config['threshold_percentage'])
    
    def test_get_config_value(self):
        """Test getting a specific configuration value"""
        config_manager = ConfigManager(self.temp_file.name)
        
        self.assertEqual(config_manager.get('refresh_rate'), 5)
        self.assertEqual(config_manager.get('nonexistent_key', 'default'), 'default')
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        with self.assertRaises(Exception):
            ConfigManager('/path/that/does/not/exist.yaml')
    
    def test_invalid_config_missing_sections(self):
        """Test handling of invalid configuration with missing sections"""
        # Create an invalid config file
        invalid_config = {
            'exchanges': [{'name': 'binance', 'enabled': True}]
            # Missing trading_pairs, refresh_rate, threshold_percentage
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(invalid_config, temp_file)
        temp_file.close()
        
        with self.assertRaises(ValueError):
            ConfigManager(temp_file.name)
        
        # Clean up
        os.unlink(temp_file.name)
    
    def test_invalid_exchanges_config(self):
        """Test handling of invalid exchanges configuration"""
        # Create an invalid config file
        invalid_config = {
            'exchanges': 'not a list',  # Should be a list
            'trading_pairs': ['SOL/USDT'],
            'refresh_rate': 5,
            'threshold_percentage': 0.5
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(invalid_config, temp_file)
        temp_file.close()
        
        with self.assertRaises(ValueError):
            ConfigManager(temp_file.name)
        
        # Clean up
        os.unlink(temp_file.name)


if __name__ == '__main__':
    unittest.main()