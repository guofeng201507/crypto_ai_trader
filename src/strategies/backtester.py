"""
Backtesting engine for evaluating trading strategies.
"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import List, Dict, Any
# Use relative imports
from .base_strategy import BaseStrategy, Signal


class Backtester:
    """Backtesting engine for trading strategies."""
    
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        """
        Initialize the backtester.
        
        Args:
            initial_capital: Initial capital for backtesting
            commission: Commission fee per trade (as a fraction)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = {}
    
    def run_backtest(self, strategy: BaseStrategy, data: pd.DataFrame, 
                     symbol: str = "BTC/USDT") -> Dict[str, Any]:
        """
        Run a backtest for a given strategy and data.
        
        Args:
            strategy: Trading strategy to test
            data: Market data with 'open', 'high', 'low', 'close', 'volume' columns
            symbol: Trading symbol
            
        Returns:
            Dictionary with backtest results
        """
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0.0  # Amount of cryptocurrency held
        equity_curve = []
        trades = []
        
        logger.info(f"Starting backtest for {strategy.name} on {symbol}")
        
        # Run through the data
        for i in range(len(data)):
            current_data = data.iloc[:i+1] if i > 0 else data.iloc[[0]]
            current_price = data.iloc[i]['close']
            
            # Generate signal
            signal = strategy.generate_signal(current_data)
            
            # Execute trades based on signals
            if signal == Signal.BUY and position == 0:
                # Buy with all capital
                amount = capital / current_price
                fee = amount * current_price * self.commission
                position = amount
                capital = 0.0
                trades.append({
                    'timestamp': data.index[i],
                    'action': 'BUY',
                    'price': current_price,
                    'amount': amount,
                    'fee': fee
                })
                logger.debug(f"BUY {amount:.6f} at {current_price:.2f}")
                
            elif signal == Signal.SELL and position > 0:
                # Sell all position
                amount = position
                fee = amount * current_price * self.commission
                capital = amount * current_price - fee
                position = 0.0
                trades.append({
                    'timestamp': data.index[i],
                    'action': 'SELL',
                    'price': current_price,
                    'amount': amount,
                    'fee': fee
                })
                logger.debug(f"SELL {amount:.6f} at {current_price:.2f}")
            
            # Calculate current equity
            equity = capital + position * current_price
            equity_curve.append(equity)
        
        # Calculate final results
        final_equity = equity_curve[-1] if equity_curve else self.initial_capital
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        max_equity = max(equity_curve) if equity_curve else self.initial_capital
        max_drawdown = min((equity - max_equity) / max_equity 
                          for equity in equity_curve) if equity_curve else 0.0
        
        results = {
            'strategy': strategy.name,
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_return_percent': total_return * 100,
            'max_drawdown': max_drawdown,
            'max_drawdown_percent': max_drawdown * 100,
            'number_of_trades': len(trades),
            'equity_curve': equity_curve,
            'trades': trades
        }
        
        self.results = results
        logger.info(f"Backtest completed. Total return: {total_return*100:.2f}%")
        
        return results
    
    def compare_strategies(self, strategies: List[BaseStrategy], data: pd.DataFrame,
                          symbol: str = "BTC/USDT") -> pd.DataFrame:
        """
        Compare multiple strategies on the same data.
        
        Args:
            strategies: List of trading strategies to compare
            data: Market data
            symbol: Trading symbol
            
        Returns:
            DataFrame with comparison results
        """
        comparison_results = []
        
        for strategy in strategies:
            results = self.run_backtest(strategy, data, symbol)
            comparison_results.append({
                'strategy': results['strategy'],
                'total_return_percent': results['total_return_percent'],
                'max_drawdown_percent': results['max_drawdown_percent'],
                'number_of_trades': results['number_of_trades']
            })
        
        return pd.DataFrame(comparison_results)


def main():
    """Example usage of the Backtester."""
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='H')
    sample_data = pd.DataFrame({
        'open': np.random.rand(100) * 50000 + 20000,
        'high': np.random.rand(100) * 50000 + 20100,
        'low': np.random.rand(100) * 50000 + 19900,
        'close': np.random.rand(100) * 50000 + 20000,
        'volume': np.random.rand(100) * 1000 + 100
    }, index=dates)
    
    # Import strategies
    from src.strategies.base_strategy import MovingAverageCrossoverStrategy, RSIStrategy
    
    # Create strategies
    ma_strategy = MovingAverageCrossoverStrategy(short_window=10, long_window=50)
    rsi_strategy = RSIStrategy()
    
    # Run backtester
    backtester = Backtester(initial_capital=10000.0)
    
    # Test single strategy
    results = backtester.run_backtest(ma_strategy, sample_data)
    print(f"MA Strategy Results: {results['total_return_percent']:.2f}% return")
    
    # Compare strategies
    strategies = [ma_strategy, rsi_strategy]
    comparison = backtester.compare_strategies(strategies, sample_data)
    print("\nStrategy Comparison:")
    print(comparison)


if __name__ == "__main__":
    main()