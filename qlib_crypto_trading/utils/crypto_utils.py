"""
Utility functions for Qlib Crypto Trading
Common helper functions used across the module
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from loguru import logger
import ccxt
from datetime import datetime, timedelta


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for crypto trading
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added technical indicators
    """
    # Ensure the DataFrame has the expected columns
    required_cols = ['$open', '$high', '$low', '$close', '$volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Simple Moving Averages
    df['sma_5'] = df['$close'].rolling(window=5).mean()
    df['sma_10'] = df['$close'].rolling(window=10).mean()
    df['sma_20'] = df['$close'].rolling(window=20).mean()
    df['sma_50'] = df['$close'].rolling(window=50).mean()
    
    # Exponential Moving Averages
    df['ema_12'] = df['$close'].ewm(span=12).mean()
    df['ema_26'] = df['$close'].ewm(span=26).mean()
    
    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # RSI
    delta = df['$close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['bb_middle'] = df['$close'].rolling(window=20).mean()
    bb_std = df['$close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_width'] = df['bb_upper'] - df['bb_lower']
    df['bb_position'] = (df['$close'] - df['bb_lower']) / df['bb_width']
    
    # Volatility (20-period standard deviation of returns)
    df['volatility'] = df['$close'].pct_change().rolling(window=20).std()
    
    # Volume indicators
    df['volume_sma'] = df['$volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['$volume'] / df['volume_sma']
    
    # Price change indicators
    df['price_change'] = df['$close'].pct_change()
    df['high_low_pct'] = (df['$high'] - df['$low']) / df['$close']
    df['open_close_pct'] = (df['$close'] - df['$open']) / df['$open']
    
    # High and low of the last n periods
    df['high_5'] = df['$high'].rolling(window=5).max()
    df['low_5'] = df['$low'].rolling(window=5).min()
    df['high_10'] = df['$high'].rolling(window=10).max()
    df['low_10'] = df['$low'].rolling(window=10).min()
    
    return df


def normalize_data(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Normalize specified columns to have zero mean and unit variance
    
    Args:
        df: Input DataFrame
        columns: List of column names to normalize
        
    Returns:
        DataFrame with normalized columns
    """
    df_normalized = df.copy()
    
    for col in columns:
        if col in df.columns:
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val != 0:  # Avoid division by zero
                df_normalized[col] = (df[col] - mean_val) / std_val
            else:
                df_normalized[col] = 0
    
    return df_normalized


def prepare_features_for_ml(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare features for machine learning models
    
    Args:
        df: DataFrame with OHLCV and technical indicators
        
    Returns:
        DataFrame with features suitable for ML models
    """
    # Calculate technical indicators if not already present
    if 'rsi' not in df.columns:
        df = calculate_technical_indicators(df)
    
    # Create target variable (next period return)
    df['target'] = df['$close'].shift(-1) / df['$close'] - 1
    
    # Select features for ML model
    feature_columns = [
        'sma_5', 'sma_10', 'sma_20', 'sma_50',
        'ema_12', 'ema_26', 'macd', 'macd_signal', 'macd_histogram',
        'rsi', 'bb_width', 'bb_position',
        'volatility', 'volume_ratio',
        'price_change', 'high_low_pct', 'open_close_pct',
        'high_5', 'low_5', 'high_10', 'low_10'
    ]
    
    # Only select features that exist in the dataframe
    available_features = [col for col in feature_columns if col in df.columns]
    
    # Create feature matrix
    features_df = df[available_features].copy()
    
    # Add lagged features
    for col in available_features:
        features_df[f'{col}_lag1'] = df[col].shift(1)
        features_df[f'{col}_lag2'] = df[col].shift(2)
    
    # Add some interaction features
    if 'rsi' in df.columns and 'bb_position' in df.columns:
        features_df['rsi_bb_position'] = df['rsi'] * df['bb_position']
    
    if '$close' in df.columns:
        features_df['log_return'] = np.log(df['$close'] / df['$close'].shift(1))
        features_df['volatility_5'] = features_df['log_return'].rolling(window=5).std()
        features_df['volatility_10'] = features_df['log_return'].rolling(window=10).std()
    
    # Add target variable
    features_df['target'] = df['target']
    
    # Drop rows with NaN values
    features_df = features_df.dropna()
    
    return features_df


def validate_crypto_symbol(symbol: str) -> bool:
    """
    Validate if a symbol is a valid crypto trading pair
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT')
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation: should contain a slash and have two parts
    if '/' not in symbol:
        return False
    
    parts = symbol.split('/')
    if len(parts) != 2:
        return False
    
    base, quote = parts
    
    # Basic checks for common crypto symbols
    if len(base) < 2 or len(base) > 10 or len(quote) < 2 or len(quote) > 10:
        return False
    
    # Check if both parts contain only alphanumeric characters and some common symbols
    import re
    if not re.match(r'^[A-Z0-9]+$', base) or not re.match(r'^[A-Z0-9]+$', quote):
        return False
    
    return True


def get_common_crypto_exchanges() -> List[str]:
    """
    Get a list of common crypto exchanges supported by CCXT
    
    Returns:
        List of exchange names
    """
    exchanges = [
        'binance', 'coinbase', 'bybit', 'huobi', 'okx', 
        'kraken', 'kucoin', 'bitfinex', 'gateio', 'mexc'
    ]
    return exchanges


def format_order_book_for_display(order_book: Dict, levels: int = 5) -> Dict:
    """
    Format order book data for display purposes
    
    Args:
        order_book: Raw order book data from exchange
        levels: Number of price levels to include
        
    Returns:
        Formatted order book data
    """
    formatted = {
        'bids': order_book['bids'][:levels],
        'asks': order_book['asks'][:levels],
        'bid_volume': sum([level[1] for level in order_book['bids'][:levels]]),
        'ask_volume': sum([level[1] for level in order_book['asks'][:levels]]),
    }
    
    # Calculate bid-ask spread
    if order_book['bids'] and order_book['asks']:
        best_bid = order_book['bids'][0][0]
        best_ask = order_book['asks'][0][0]
        spread = best_ask - best_bid
        spread_pct = (spread / ((best_bid + best_ask) / 2)) * 100
        formatted['spread'] = spread
        formatted['spread_pct'] = spread_pct
    
    return formatted


def calculate_portfolio_metrics(
    returns: pd.Series, 
    risk_free_rate: float = 0.02
) -> Dict[str, float]:
    """
    Calculate portfolio performance metrics
    
    Args:
        returns: Series of portfolio returns
        risk_free_rate: Risk-free rate for Sharpe ratio calculation
        
    Returns:
        Dictionary of performance metrics
    """
    # Remove NaN values
    returns = returns.dropna()
    
    if len(returns) == 0:
        return {}
    
    # Total return
    total_return = (1 + returns).prod() - 1
    
    # Annualized return (assuming daily returns)
    avg_return = returns.mean()
    annual_return = avg_return * 252  # 252 trading days in a year
    
    # Volatility (annualized)
    volatility = returns.std() * np.sqrt(252)
    
    # Sharpe ratio
    if volatility != 0:
        sharpe_ratio = (annual_return - risk_free_rate) / volatility
    else:
        sharpe_ratio = np.nan
    
    # Maximum drawdown
    cum_returns = (1 + returns).cumprod()
    rolling_max = cum_returns.expanding().max()
    drawdown = (cum_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    # Calmar ratio (return over max drawdown)
    if max_drawdown != 0:
        calmar_ratio = annual_return / abs(max_drawdown)
    else:
        calmar_ratio = np.nan
    
    # Value at Risk (VaR) at 5% confidence level
    var_5 = returns.quantile(0.05)
    
    # Sortino ratio (downside deviation)
    negative_returns = returns[returns < 0]
    if len(negative_returns) > 0:
        downside_deviation = negative_returns.std() * np.sqrt(252)
        if downside_deviation != 0:
            sortino_ratio = (annual_return - risk_free_rate) / downside_deviation
        else:
            sortino_ratio = np.nan
    else:
        sortino_ratio = np.inf  # No negative returns
    
    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'calmar_ratio': calmar_ratio,
        'var_5': var_5,
        'sortino_ratio': sortino_ratio
    }


def convert_timestamp_to_datetime(timestamp: float, unit: str = 'milliseconds') -> datetime:
    """
    Convert timestamp to datetime object
    
    Args:
        timestamp: Numeric timestamp
        unit: Unit of the timestamp ('milliseconds' or 'seconds')
        
    Returns:
        datetime object
    """
    if unit == 'milliseconds':
        return datetime.fromtimestamp(timestamp / 1000)
    elif unit == 'seconds':
        return datetime.fromtimestamp(timestamp)
    else:
        raise ValueError("Unit must be 'milliseconds' or 'seconds'")


def calculate_position_size(
    account_balance: float,
    risk_percentage: float,
    entry_price: float,
    stop_loss_price: float
) -> float:
    """
    Calculate position size based on risk management parameters
    
    Args:
        account_balance: Total account balance
        risk_percentage: Percentage of account to risk (e.g., 0.02 for 2%)
        entry_price: Entry price for the trade
        stop_loss_price: Stop loss price for the trade
        
    Returns:
        Position size in units of the base currency
    """
    # Calculate risk amount in quote currency
    risk_amount = account_balance * risk_percentage
    
    # Calculate stop loss distance
    stop_distance = abs(entry_price - stop_loss_price)
    
    if stop_distance == 0:
        raise ValueError("Stop loss price cannot equal entry price")
    
    # Calculate position size
    position_size = risk_amount / stop_distance
    
    # Ensure position size does not exceed account balance
    max_size_by_balance = account_balance / entry_price
    position_size = min(position_size, max_size_by_balance)
    
    return position_size


if __name__ == "__main__":
    # Example usage
    logger.info("Utility functions loaded successfully")
    
    # Example: create a sample dataframe and calculate indicators
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    sample_df = pd.DataFrame({
        '$open': np.random.rand(100) * 100 + 40000,
        '$high': np.random.rand(100) * 100 + 40100,
        '$low': np.random.rand(100) * 100 + 39900,
        '$close': np.random.rand(100) * 100 + 40050,
        '$volume': np.random.rand(100) * 1000 + 100
    }, index=dates)
    
    indicators_df = calculate_technical_indicators(sample_df)
    logger.info(f"Calculated technical indicators. Shape: {indicators_df.shape}")
    
    features_df = prepare_features_for_ml(indicators_df)
    logger.info(f"Prepared features for ML. Shape: {features_df.shape}")
    
    print("Utility functions work correctly!")