"""
Configuration manager utility
"""
import yaml
import os


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
        """
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config file {self.config_file}: {e}")
            raise
    
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