"""
Strategies module for the Crypto AI Trader.
"""

from .base_strategy import BaseStrategy, Signal
from .scalping_strategy import ScalpingStrategy
from .backtester import Backtester
from .trader import Trader
from .risk_manager import RiskManager

__all__ = [
    'BaseStrategy',
    'Signal',
    'ScalpingStrategy',
    'Backtester',
    'Trader',
    'RiskManager'
]