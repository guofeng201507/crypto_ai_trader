"""
Configuration manager utility
"""
import yaml
import os
from loguru import logger


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file):
        """
        Initialize the ConfigManager
        
        Args:
            config_file (str): Path to the configuration file
        """
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to project root, then to config file
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.config_file = os.path.join(project_root, config_file)
        self.config = self.load_config()
    
    def load_config(self):
        """
        Load configuration from YAML file
        
        Returns:
            dict: Configuration dictionary
            
        Raises:
            Exception: If there's an error loading the configuration
        """
        try:
            with open(self.config_file, 'r') as file:
                config = yaml.safe_load(file)
                # Validate required configuration
                self._validate_config(config)
                return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_file}")
            raise Exception(f"Config file not found: {self.config_file}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML in config file {self.config_file}: {e}")
            raise Exception(f"Error parsing YAML in config file {self.config_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading config file {self.config_file}: {e}")
            raise Exception(f"Error loading config file {self.config_file}: {e}")
    
    def _validate_config(self, config):
        """
        Validate the configuration has required fields
        
        Args:
            config (dict): Configuration dictionary
            
        Raises:
            ValueError: If required configuration is missing
        """
        required_sections = ['exchanges', 'trading_pairs', 'refresh_rate', 'threshold_percentage']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate exchanges
        if not isinstance(config['exchanges'], list):
            raise ValueError("Exchanges configuration must be a list")
        
        # Validate trading pairs
        if not isinstance(config['trading_pairs'], list):
            raise ValueError("Trading pairs configuration must be a list")
        
        # Validate refresh rate
        if not isinstance(config['refresh_rate'], (int, float)) or config['refresh_rate'] <= 0:
            raise ValueError("Refresh rate must be a positive number")
        
        # Validate threshold percentage
        if not isinstance(config['threshold_percentage'], (int, float)) or config['threshold_percentage'] < 0:
            raise ValueError("Threshold percentage must be a non-negative number")
    
    def get_config(self):
        """
        Get the configuration dictionary
        
        Returns:
            dict: Configuration dictionary
        """
        return self.config
    
    def get(self, key, default=None):
        """
        Get a configuration value by key
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)