"""
Configuration manager for the 3-month high tracker
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manages configuration for the 3-month high tracker
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or 'config/price_monitor_config.yaml'
        self.default_config = self._get_default_config()
        self.config = self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values
        
        Returns:
            Default configuration dictionary
        """
        return {
            'exchanges': ['binance'],
            'trading_pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT'],
            'drop_threshold': 0.20,  # 20% drop
            'refresh_rate': 60,      # seconds
            'data_dir': 'data/',
            'price_history_days': 90,  # 3 months
            'timeframe': '1d',
            'notification_methods': ['console'],
            'email': {
                'smtp_server': '',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipients': []
            },
            'discord_webhook_url': '',
            'telegram_bot_token': '',
            'telegram_chat_id': ''
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file, using defaults for missing values
        
        Returns:
            Loaded configuration dictionary
        """
        config = self.default_config.copy()
        
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        # Update default config with user config, preserving nested structures
                        self._deep_update(config, user_config)
            except Exception as e:
                print(f"Could not load config from {self.config_path}: {e}. Using defaults.")
        
        return config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """
        Recursively update a nested dictionary
        
        Args:
            base_dict: Base dictionary to update
            update_dict: Dictionary with updates
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self, config: Optional[Dict] = None):
        """
        Save configuration to file
        
        Args:
            config: Configuration to save (uses current config if None)
        """
        if config is None:
            config = self.config
        
        config_file = Path(self.config_path)
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation for nested keys
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value using dot notation for nested keys
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        config_ref = self.config
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value