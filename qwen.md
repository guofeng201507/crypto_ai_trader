# Qwen Code — Python Coding Standards for Quantitative Trading & AI Agent Development

> Purpose: Establish comprehensive Python coding standards for quantitative trading systems and AI agent development, following best practices from top quantitative trading firms. This guide ensures code quality, maintainability, performance, and reliability for algorithmic trading systems.

---

## 1. Code Structure and Organization

### 1.1 Project Layout
```
project/
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── environments/
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py
│   │   └── preprocessors.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── strategies.py
│   │   └── risk_models.py
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── broker_interfaces.py
│   │   └── order_manager.py
│   ├── risk/
│   │   ├── __init__.py
│   │   ├── limits.py
│   │   └── monitoring.py
│   ├── backtesting/
│   │   ├── __init__.py
│   │   └── engine.py
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py
│       ├── metrics.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── backtesting/
├── notebooks/  # For research and analysis
└── logs/
```

### 1.2 Module Organization
- Use clear, descriptive names for modules and packages
- Maintain consistent naming conventions throughout the project
- Group related functionality in cohesive modules
- Separate configuration, data, models, execution, and backtesting logic

## 2. Python Language Standards

### 2.1 Type Hints and Static Analysis
```python
from typing import Optional, Dict, List, Union, Callable, TypeVar
from datetime import datetime
import numpy as np
import pandas as pd

def calculate_sharpe_ratio(
    returns: pd.Series, 
    risk_free_rate: float = 0.0
) -> float:
    """
    Calculate the Sharpe ratio for a series of returns.
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate to subtract from returns (default 0.0)
        
    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)  # Annualized
```

- Use type hints for all functions, methods, and class attributes
- Run mypy for static type checking with strict settings
- Use TypedDict for complex dictionary structures
- Utilize Protocol for structural subtyping where appropriate

### 2.2 Code Formatting
- Follow PEP 8 guidelines with 4-space indentation
- Use Black for automatic code formatting
- Set line length to 88 characters (Black default)
- Use isort for import organization
- Maintain consistent naming conventions

### 2.3 Import Organization
```python
# Standard library imports
from datetime import datetime
from typing import Dict, List
import os
import sys

# Third-party imports
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Local application/library imports
from src.models.strategies import BaseStrategy
from src.utils.metrics import calculate_sharpe_ratio
```

## 3. Data Handling & Performance

### 3.1 Data Structures
- Use pandas for data manipulation and analysis
- Leverage NumPy for numerical computations
- Consider Dask for large datasets that don't fit in memory
- Use proper data types (e.g., category for strings, int64/float64 for numbers)
- Implement proper date/time handling with timezone awareness

### 3.2 Performance Optimization
```python
# Use vectorized operations when possible
def vectorized_calculation(prices: pd.Series) -> pd.Series:
    # Good - vectorized
    returns = prices.pct_change()
    return returns
    
def non_vectorized_calculation(prices: pd.Series) -> pd.Series:
    # Avoid - loops are slow
    returns = []
    for i in range(1, len(prices)):
        returns.append((prices[i] - prices[i-1]) / prices[i-1])
    return pd.Series(returns, index=prices.index[1:])
```

- Prioritize vectorized operations over loops
- Use numba for computational bottlenecks
- Profile code using cProfile or line_profiler
- Use memory-efficient data structures and operations

### 3.3 Memory Management
- Explicitly delete large objects when no longer needed
- Use generators for processing large datasets
- Implement proper garbage collection strategies

## 4. Error Handling and Robustness

### 4.1 Exception Handling
```python
import logging
from typing import Optional

def fetch_market_data(symbol: str) -> Optional[pd.DataFrame]:
    """
    Fetch market data for a given symbol.
    
    Args:
        symbol: Trading symbol to fetch data for
        
    Returns:
        DataFrame with market data or None if error
    """
    try:
        # Data fetching logic here
        data = api_client.get_data(symbol)
        return data
    except APIException as e:
        logging.error(f"API error while fetching data for {symbol}: {str(e)}")
        return None
    except ValueError as e:
        logging.error(f"Data validation error for {symbol}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error while fetching data for {symbol}: {str(e)}")
        return None
```

- Implement specific exception handling for different error types
- Log errors with appropriate severity levels
- Implement retry mechanisms for transient failures
- Design for graceful degradation

### 4.2 Input Validation
```python
def validate_order(order_params: Dict) -> bool:
    """
    Validate order parameters before execution.
    
    Args:
        order_params: Dictionary containing order parameters
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['symbol', 'side', 'quantity', 'price']
    for field in required_fields:
        if field not in order_params:
            raise ValueError(f"Missing required field: {field}")
    
    if order_params['quantity'] <= 0:
        raise ValueError("Quantity must be positive")
        
    if order_params['price'] <= 0:
        raise ValueError("Price must be positive")
        
    return True
```

## 5. Testing and Verification

### 5.1 Testing Strategy
- 100% test coverage for critical trading logic
- Unit tests for all functions and methods
- Integration tests for end-to-end trading workflows
- Backtesting validation against historical data
- Stress testing with various market conditions

### 5.2 Test Examples
```python
import pytest
import pandas as pd
from src.models.strategies import MeanReversionStrategy

def test_calculate_position_size():
    """Test position sizing logic"""
    strategy = MeanReversionStrategy()
    result = strategy.calculate_position_size(
        price=100.0,
        account_balance=10000.0,
        risk_percentage=0.02
    )
    expected = 200.0  # 2% of $10,000 at $100 price = 2 shares
    assert result == expected

def test_strategy_signal_generation():
    """Test that strategy generates valid signals"""
    strategy = MeanReversionStrategy()
    data = pd.DataFrame({
        'close': [100, 102, 101, 98, 97, 99, 101],
        'sma': [101, 101, 101, 100, 100, 100, 100]
    })
    signals = strategy.generate_signals(data)
    
    # Verify signal structure and valid values
    assert 'signal' in signals.columns
    assert all(signal in [-1, 0, 1] for signal in signals['signal'])
```

## 6. Logging and Monitoring

### 6.1 Logging Standards
- Use structured logging with JSON format for production
- Include request IDs, session IDs, and other correlation IDs
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include performance metrics in logs when appropriate

### 6.2 Log Examples
```python
import logging
import json
from datetime import datetime

def log_trade_execution(order_id: str, symbol: str, quantity: float, price: float):
    """Log trade execution details"""
    log_data = {
        'event': 'trade_execution',
        'order_id': order_id,
        'symbol': symbol,
        'quantity': quantity,
        'price': price,
        'timestamp': datetime.utcnow().isoformat(),
        'execution_type': 'market'
    }
    logging.info(json.dumps(log_data))
```

## 7. Risk Management

### 7.1 Risk Controls
- Implement position limits and stop-losses
- Validate all positions against risk parameters
- Monitor portfolio exposure and concentration
- Implement circuit breakers for extreme market conditions

### 7.2 Risk Metrics
- Calculate Value at Risk (VaR) and Expected Shortfall
- Monitor portfolio Greeks for options positions
- Track drawdown and maximum adverse excursion
- Implement real-time risk monitoring

## 8. AI Agent Development Standards

### 8.1 Agent Architecture
- Define clear observation, action, and reward spaces
- Maintain separation between environment and agent logic
- Implement proper state management and reset functionality
- Use well-defined interfaces between components

### 8.2 Model Training and Validation
- Implement proper train/validation/test splits
- Use walk-forward analysis for time series data
- Validate models on out-of-sample data
- Monitor for overfitting and data leakage

### 8.3 Agent Example
```python
import numpy as np
import pandas as pd
from typing import Tuple

class TradingAgent:
    """Base class for trading agents"""
    
    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        self.model = self._build_model()
        
    def _build_model(self):
        """Build the agent's model"""
        # Model building logic here
        pass
        
    def act(self, state: np.ndarray) -> Tuple[int, float]:
        """
        Take action based on current state.
        
        Args:
            state: Current market state
            
        Returns:
            (action, confidence) tuple
        """
        # Agent action logic
        pass
        
    def train(self, experiences: List[Tuple]) -> float:
        """
        Train the agent on experiences.
        
        Args:
            experiences: List of (state, action, reward, next_state, done) tuples
            
        Returns:
            Training loss
        """
        # Training logic
        pass
```

## 9. Configuration Management

### 9.1 Environment Configuration
- Use environment variables for sensitive information
- Store configuration in YAML/JSON files
- Implement different configurations for development, staging, and production
- Validate configuration values at startup

### 9.2 Configuration Example
```yaml
# config/production.yaml
trading:
  max_position_size: 10000
  max_drawdown: 0.05
  slippage_tolerance: 0.001
  api_rate_limit: 5  # requests per second

risk:
  max_daily_loss: 0.02
  max_position_concentration: 0.10
  circuit_breaker_threshold: 0.03

logging:
  level: INFO
  format: json
  output: file
```

## 10. Deployment and Infrastructure

### 10.1 Containerization
- Use Docker for consistent deployment environments
- Implement multi-stage builds to minimize image size
- Implement health checks for services
- Use environment-specific Docker Compose files

### 10.2 CI/CD Pipeline
- Implement automated testing for all code changes
- Run static analysis tools (mypy, flake8, black)
- Implement automated deployment to staging
- Use feature flags for safe rollouts

### 10.3 Infrastructure as Code
- Use Terraform or CloudFormation for infrastructure provisioning
- Implement proper secret management
- Implement proper backup and disaster recovery procedures

## 11. Security Standards

### 11.1 Secret Management
- Never hardcode API keys or sensitive information
- Use environment variables or secret management systems
- Implement proper key rotation procedures
- Follow principle of least privilege for all services

### 11.2 Secure Coding Practices
- Validate all inputs to prevent injection attacks
- Implement proper authentication and authorization
- Use secure communication protocols (HTTPS, TLS)
- Sanitize and validate all data from external sources

## 12. Documentation Standards

### 12.1 Code Documentation
- Document all public functions, classes, and modules with docstrings
- Use Google or NumPy docstring format consistently
- Include examples in documentation where helpful
- Maintain a comprehensive README with setup instructions

### 12.2 Architecture Documentation
- Document system architecture with diagrams
- Explain data flow and component interactions
- Document deployment procedures
- Maintain API documentation

## 13. Best Practices from Top Trading Firms

### 13.1 Goldman Sachs Approach
- Emphasis on code review and pair programming
- Extensive automated testing and validation
- Focus on code quality metrics and technical debt management

### 13.2 Renaissance Technologies Approach
- Heavy emphasis on data quality and validation
- Rigorous backtesting with proper statistical significance
- Focus on algorithmic efficiency and optimization

### 13.3 Two Sigma Approach
- Integration of machine learning best practices
- Strong emphasis on reproducibility and version control
- Collaborative development tools and workflows

### 13.4 Citadel Approach
- Risk-first development methodology
- Real-time monitoring and alerting systems
- Performance optimization and low-latency requirements

---

> Version: 1.0 — This document represents best practices from top quantitative trading firms and should be customized based on your specific requirements and compliance needs.