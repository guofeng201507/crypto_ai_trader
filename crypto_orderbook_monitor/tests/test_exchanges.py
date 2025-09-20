"""
Unit tests for the exchange classes
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exchanges.base_exchange import BaseExchange
from exchanges.binance import BinanceExchange
from exchanges.okx import OkxExchange
from exchanges.coinbase import CoinbaseExchange


class TestBaseExchange(unittest.TestCase):
    """Test cases for the BaseExchange class"""
    
    def test_base_exchange_initialization(self):
        """Test BaseExchange initialization"""
        exchange = BaseExchange("test_exchange")
        self.assertEqual(exchange.name, "test_exchange")
        self.assertIsNone(exchange.exchange)
    
    def test_base_exchange_abstract_methods(self):
        """Test that BaseExchange has abstract methods"""
        exchange = BaseExchange("test_exchange")
        
        # fetch_orderbook should be abstract
        with self.assertRaises(NotImplementedError):
            exchange.fetch_orderbook("SOL/USDT")


class TestBinanceExchange(unittest.TestCase):
    """Test cases for the BinanceExchange class"""
    
    def test_binance_initialization(self):
        """Test BinanceExchange initialization"""
        with patch('exchanges.binance.ccxt') as mock_ccxt:
            mock_binance = Mock()
            mock_ccxt.binance.return_value = mock_binance
            
            exchange = BinanceExchange()
            self.assertEqual(exchange.name, "binance")
            self.assertIsNotNone(exchange.exchange)
    
    @patch('exchanges.binance.ccxt')
    def test_binance_fetch_orderbook_success(self, mock_ccxt):
        """Test BinanceExchange fetch_orderbook success"""
        mock_binance = Mock()
        mock_ccxt.binance.return_value = mock_binance
        mock_binance.markets = {'SOL/USDT': {}}
        mock_orderbook = {
            'bids': [[100.0, 1.0]],
            'asks': [[101.0, 1.0]]
        }
        mock_binance.fetch_order_book.return_value = mock_orderbook
        
        exchange = BinanceExchange()
        result = exchange.fetch_orderbook("SOL/USDT")
        
        self.assertEqual(result, mock_orderbook)
        mock_binance.fetch_order_book.assert_called_once_with("SOL/USDT", limit=50)
    
    @patch('exchanges.binance.ccxt')
    def test_binance_fetch_orderbook_symbol_not_found(self, mock_ccxt):
        """Test BinanceExchange fetch_orderbook with invalid symbol"""
        mock_binance = Mock()
        mock_ccxt.binance.return_value = mock_binance
        mock_binance.markets = {'BTC/USDT': {}}
        
        exchange = BinanceExchange()
        
        with self.assertRaises(Exception) as context:
            exchange.fetch_orderbook("INVALID/PAIR")
        
        self.assertIn("Symbol INVALID/PAIR not available on Binance", str(context.exception))


class TestOkxExchange(unittest.TestCase):
    """Test cases for the OkxExchange class"""
    
    def test_okx_initialization(self):
        """Test OkxExchange initialization"""
        with patch('exchanges.okx.ccxt') as mock_ccxt:
            mock_okx = Mock()
            mock_ccxt.okx.return_value = mock_okx
            
            exchange = OkxExchange()
            self.assertEqual(exchange.name, "okx")
            self.assertIsNotNone(exchange.exchange)


class TestCoinbaseExchange(unittest.TestCase):
    """Test cases for the CoinbaseExchange class"""
    
    def test_coinbase_initialization(self):
        """Test CoinbaseExchange initialization"""
        with patch('exchanges.coinbase.ccxt') as mock_ccxt:
            mock_coinbase = Mock()
            mock_ccxt.coinbase.return_value = mock_coinbase
            
            exchange = CoinbaseExchange()
            self.assertEqual(exchange.name, "coinbase")
            self.assertIsNotNone(exchange.exchange)


if __name__ == '__main__':
    unittest.main()