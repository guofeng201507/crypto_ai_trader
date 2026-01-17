"""Unit tests for ThreeMonthHighTracker."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from crypto_price_monitor.high_tracker import ThreeMonthHighTracker


class TestThreeMonthHighTracker(unittest.TestCase):
    """Test cases for ThreeMonthHighTracker."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'exchanges': ['binance'],
            'trading_pairs': ['BTC/USDT'],
            'drop_threshold': 0.20,
            'refresh_rate': 60,
            'data_dir': self.temp_dir,
            'notification_methods': ['console'],
            'price_history_days': 90
        }

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('crypto_price_monitor.high_tracker.DataFetcher')
    def test_init(self, mock_fetcher):
        """Test tracker initialization."""
        tracker = ThreeMonthHighTracker()
        self.assertIsNotNone(tracker)
        self.assertIsInstance(tracker.highs_cache, dict)
        self.assertIsInstance(tracker.price_cache, dict)

    def test_load_config_default(self):
        """Test loading default configuration."""
        tracker = ThreeMonthHighTracker()
        config = tracker.config
        self.assertIn('exchanges', config)
        self.assertIn('trading_pairs', config)
        self.assertEqual(config['drop_threshold'], 0.20)

    def test_calculate_three_month_high(self):
        """Test calculation of 3-month high."""
        tracker = ThreeMonthHighTracker()
        
        # Create sample price data
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        data = pd.DataFrame({
            'high': [100 + i for i in range(90)],
            'close': [99 + i for i in range(90)]
        }, index=dates)
        
        high_price, high_date = tracker.calculate_three_month_high(data)
        self.assertEqual(high_price, 189.0)  # 100 + 89
        self.assertIsInstance(high_date, pd.Timestamp)

    def test_calculate_three_month_high_empty_data(self):
        """Test calculation with empty DataFrame."""
        tracker = ThreeMonthHighTracker()
        data = pd.DataFrame()
        
        high_price, high_date = tracker.calculate_three_month_high(data)
        self.assertEqual(high_price, 0.0)
        self.assertIsInstance(high_date, datetime)

    def test_is_drop_alert_true(self):
        """Test drop alert detection when price dropped enough."""
        tracker = ThreeMonthHighTracker()
        
        current_price = 80.0
        three_month_high = 100.0
        
        result = tracker.is_drop_alert(current_price, three_month_high)
        self.assertTrue(result)  # 20% drop

    def test_is_drop_alert_false(self):
        """Test drop alert when price hasn't dropped enough."""
        tracker = ThreeMonthHighTracker()
        
        current_price = 85.0
        three_month_high = 100.0
        
        result = tracker.is_drop_alert(current_price, three_month_high)
        self.assertFalse(result)  # Only 15% drop

    def test_is_drop_alert_zero_high(self):
        """Test drop alert with zero high price."""
        tracker = ThreeMonthHighTracker()
        
        current_price = 80.0
        three_month_high = 0.0
        
        result = tracker.is_drop_alert(current_price, three_month_high)
        self.assertFalse(result)

    @patch('crypto_price_monitor.high_tracker.DataFetcher')
    def test_get_current_price(self, mock_fetcher_class):
        """Test getting current price."""
        mock_fetcher = Mock()
        mock_fetcher.get_current_price.return_value = 50000.0
        mock_fetcher_class.return_value = mock_fetcher
        
        tracker = ThreeMonthHighTracker()
        tracker.data_fetcher = mock_fetcher
        
        price = tracker.get_current_price('binance', 'BTC/USDT')
        self.assertEqual(price, 50000.0)
        mock_fetcher.get_current_price.assert_called_once_with('binance', 'BTC/USDT')

    @patch('crypto_price_monitor.high_tracker.DataFetcher')
    def test_check_price_drop_no_alert(self, mock_fetcher_class):
        """Test check_price_drop when no alert needed."""
        mock_fetcher = Mock()
        mock_fetcher.get_current_price.return_value = 90.0
        mock_fetcher_class.return_value = mock_fetcher
        
        tracker = ThreeMonthHighTracker()
        tracker.data_fetcher = mock_fetcher
        tracker.exchange_instances = {'binance': Mock()}
        tracker.highs_cache['binance_BTC/USDT'] = {
            'high': 100.0,
            'timestamp': datetime.now().isoformat()
        }
        
        result = tracker.check_price_drop('binance', 'BTC/USDT')
        self.assertIsNone(result)

    @patch('crypto_price_monitor.high_tracker.DataFetcher')
    def test_check_price_drop_with_alert(self, mock_fetcher_class):
        """Test check_price_drop when alert is triggered."""
        mock_fetcher = Mock()
        mock_fetcher.get_current_price.return_value = 75.0
        mock_fetcher_class.return_value = mock_fetcher
        
        tracker = ThreeMonthHighTracker()
        tracker.data_fetcher = mock_fetcher
        tracker.exchange_instances = {'binance': Mock()}
        tracker.highs_cache['binance_BTC/USDT'] = {
            'high': 100.0,
            'timestamp': datetime.now().isoformat()
        }
        
        result = tracker.check_price_drop('binance', 'BTC/USDT')
        self.assertIsNotNone(result)
        self.assertEqual(result['exchange'], 'binance')
        self.assertEqual(result['symbol'], 'BTC/USDT')
        self.assertEqual(result['current_price'], 75.0)


if __name__ == '__main__':
    unittest.main()
