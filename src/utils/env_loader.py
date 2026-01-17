"""Environment variable loader utility.

All modules use this utility to load from the root .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger


def get_project_root() -> Path:
    """Find the project root directory (where .env is located)."""
    current = Path(__file__).resolve()
    # Go up from src/utils/env_loader.py to project root
    return current.parent.parent.parent


def load_environment_variables(env_file: str = None):
    """Load environment variables from the root .env file.
    
    Args:
        env_file: Optional path to env file. If None, uses project root .env
    """
    if env_file is None:
        # Always use root .env file
        project_root = get_project_root()
        env_file = project_root / ".env"
    
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Environment variables loaded from {env_file}")
    else:
        logger.warning(f"Environment file {env_file} not found")


def get_env_variable(var_name: str, default_value: str = None) -> str:
    """
    Get an environment variable value.
    
    Args:
        var_name: Name of the environment variable
        default_value: Default value if variable is not set
        
    Returns:
        Value of the environment variable
    """
    return os.getenv(var_name, default_value)


def main():
    """Example usage of the environment loader."""
    # Load environment variables
    load_environment_variables()
    
    # Get some environment variables
    trading_mode = get_env_variable("TRADING_MODE", "Paper")
    initial_capital = get_env_variable("INITIAL_CAPITAL", "10000.0")
    
    print(f"Trading Mode: {trading_mode}")
    print(f"Initial Capital: {initial_capital}")


if __name__ == "__main__":
    main()