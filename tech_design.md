# Crypto Orderbook Monitor - Technical Documentation

## Project Overview

The Crypto Orderbook Monitor is a Python application that monitors orderbooks from multiple cryptocurrency exchanges (Binance, OKX, Coinbase) and detects price discrepancies for arbitrage opportunities. The application provides real-time monitoring with enhanced accuracy through weighted price calculations and robust error handling.

## Project Structure

```
crypto_orderbook_monitor/
├── main.py                      # Entry point and main monitoring logic
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
├── README.md                    # User documentation
├── coding.md                    # Development documentation
├── tests/                       # Unit tests
│   ├── requirements.txt         # Test dependencies
│   ├── test_config_manager.py   # Tests for configuration management
│   ├── test_discrepancy_detection.py  # Tests for discrepancy detection
│   └── test_exchanges.py        # Tests for exchange implementations
└── src/                         # Source code
    ├── __init__.py              # Package initialization
    ├── main.py                  # Main application logic (symlink or copy)
    ├── exchanges/               # Exchange implementations
    │   ├── __init__.py          # Package initialization
    │   ├── base_exchange.py     # Abstract base class for exchanges
    │   ├── binance.py           # Binance exchange implementation
    │   ├── okx.py               # OKX exchange implementation
    │   └── coinbase.py          # Coinbase exchange implementation
    └── utils/                   # Utility modules
        ├── __init__.py          # Package initialization
        └── config_manager.py    # Configuration management
```

## File Descriptions

### Root Directory Files

#### `main.py`
**Purpose**: Entry point and main application logic
**Key Functions**:
- `main()`: Orchestrates the entire application flow
- `signal_handler()`: Handles shutdown signals for graceful termination
- `detect_discrepancies()`: Analyzes orderbooks to detect arbitrage opportunities
- `calculate_weighted_price()`: Calculates weighted average prices for more accurate profit estimation

**Features**:
- Configuration loading and validation
- Exchange initialization and management
- Real-time orderbook monitoring
- Arbitrage detection with enhanced accuracy
- Graceful shutdown with resource cleanup
- Comprehensive logging

#### `config.yaml`
**Purpose**: Application configuration file
**Sections**:
- `exchanges`: List of exchanges with enable/disable flags
- `trading_pairs`: List of trading pairs to monitor
- `refresh_rate`: Time interval between monitoring cycles (in seconds)
- `threshold_percentage`: Minimum price difference percentage to trigger alerts
- `log_level`: Logging verbosity level
- `log_file`: Path to the log file

#### `requirements.txt`
**Purpose**: Lists Python dependencies required for the application
**Key Dependencies**:
- `ccxt`: Cryptocurrency exchange library
- `pandas`: Data manipulation library
- `numpy`: Numerical computing library
- `loguru`: Enhanced logging library
- `asyncio`: Asynchronous I/O library
- `websockets`: WebSocket client/server implementation

#### `README.md`
**Purpose**: User documentation providing instructions for installation, configuration, and usage

#### `coding.md`
**Purpose**: Development documentation detailing the refactoring work and technical improvements

### Tests Directory

#### `tests/requirements.txt`
**Purpose**: Lists Python dependencies required for running tests
**Additional Dependencies**:
- `pytest`: Testing framework
- `pytest-asyncio`: Pytest plugin for async testing

#### `tests/test_config_manager.py`
**Purpose**: Unit tests for the configuration manager
**Test Cases**:
- Loading valid configuration files
- Handling missing configuration files
- Validating configuration structure
- Testing configuration value retrieval

#### `tests/test_discrepancy_detection.py`
**Purpose**: Unit tests for discrepancy detection algorithms
**Test Cases**:
- Weighted price calculation with various orderbook scenarios
- Discrepancy detection with and without arbitrage opportunities
- Edge cases for price calculation functions

#### `tests/test_exchanges.py`
**Purpose**: Unit tests for exchange implementations
**Test Cases**:
- Exchange class initialization
- Orderbook fetching functionality
- Error handling scenarios
- Abstract method implementation verification

### Source Code Directory (`src/`)

#### `src/exchanges/base_exchange.py`
**Purpose**: Abstract base class defining the interface for all exchange implementations
**Key Components**:
- `BaseExchange` class with abstract methods:
  - `fetch_orderbook()`: Abstract method for fetching orderbook data
  - `close()`: Method for closing exchange connections

#### `src/exchanges/binance.py`
**Purpose**: Binance exchange implementation
**Key Components**:
- `BinanceExchange` class extending `BaseExchange`
- `__init__()`: Initializes Binance exchange with rate limiting and timeout
- `fetch_orderbook()`: Fetches orderbook data from Binance with error handling
- `close()`: Closes Binance exchange connection

**Features**:
- Symbol validation
- Rate limiting
- Timeout configuration (10 seconds)
- Orderbook depth limiting (50 levels)
- Comprehensive error handling for network, exchange, and value errors

#### `src/exchanges/okx.py`
**Purpose**: OKX exchange implementation
**Key Components**:
- `OkxExchange` class extending `BaseExchange`
- `__init__()`: Initializes OKX exchange with rate limiting and timeout
- `fetch_orderbook()`: Fetches orderbook data from OKX with symbol format handling
- `close()`: Closes OKX exchange connection

**Features**:
- Symbol format conversion (handling different naming conventions)
- Symbol lookup for alternative naming
- Rate limiting
- Timeout configuration (10 seconds)
- Orderbook depth limiting (50 levels)
- Comprehensive error handling

#### `src/exchanges/coinbase.py`
**Purpose**: Coinbase exchange implementation
**Key Components**:
- `CoinbaseExchange` class extending `BaseExchange`
- `__init__()`: Initializes Coinbase exchange with rate limiting and timeout
- `fetch_orderbook()`: Fetches orderbook data from Coinbase with symbol format handling
- `close()`: Closes Coinbase exchange connection

**Features**:
- Symbol format conversion (slashes to hyphens)
- Symbol lookup for alternative naming
- Rate limiting
- Timeout configuration (10 seconds)
- Orderbook depth limiting (50 levels)
- Comprehensive error handling

#### `src/utils/config_manager.py`
**Purpose**: Configuration management utility
**Key Components**:
- `ConfigManager` class:
  - `__init__()`: Initializes configuration manager with file path
  - `load_config()`: Loads and parses YAML configuration file
  - `_validate_config()`: Validates configuration structure and required fields
  - `get_config()`: Returns the loaded configuration dictionary
  - `get()`: Retrieves specific configuration values with default support

**Features**:
- YAML file parsing
- Configuration validation
- Error handling for missing or invalid files
- Default value support for configuration retrieval

## Application Flow

1. **Initialization**:
   - Load configuration from `config.yaml`
   - Set up logging with `loguru`
   - Initialize exchange connections based on configuration

2. **Monitoring Loop**:
   - Fetch orderbooks from all enabled exchanges for configured trading pairs
   - Detect price discrepancies using enhanced algorithm
   - Calculate weighted prices for more accurate profit estimation
   - Log and display arbitrage opportunities
   - Wait for configured refresh period

3. **Shutdown**:
   - Handle SIGINT/SIGTERM signals
   - Close all exchange connections
   - Clean up resources

## Key Features

1. **Multi-Exchange Support**: Binance, OKX, and Coinbase
2. **Real-Time Monitoring**: Continuous orderbook monitoring
3. **Enhanced Accuracy**: Weighted price calculations considering orderbook depth
4. **Robust Error Handling**: Comprehensive error handling for network and exchange issues
5. **Graceful Shutdown**: Proper resource cleanup on termination
6. **Configurable**: YAML-based configuration
7. **Comprehensive Logging**: Detailed logging to file and console
8. **Unit Testing**: Complete test suite for all components
9. **Kill Switch**: Emergency stopping mechanism

## Development Guidelines

1. **Code Style**: Follow PEP8 guidelines
2. **Error Handling**: Implement specific exception handling
3. **Logging**: Use `loguru` for consistent logging
4. **Testing**: Write unit tests for new functionality
5. **Documentation**: Update documentation with code changes
6. **Configuration**: Use `config.yaml` for all configurable parameters

This documentation provides a comprehensive overview of the Crypto Orderbook Monitor application structure and functionality, enabling developers to understand, maintain, and extend the system effectively.