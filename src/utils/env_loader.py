"""
Environment variable loader utility.
"""
import os
from dotenv import load_dotenv
from loguru import logger


def load_environment_variables(env_file: str = ".env"):
    """
    Load environment variables from a file.
    
    Args:
        env_file: Path to the environment file
    """
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