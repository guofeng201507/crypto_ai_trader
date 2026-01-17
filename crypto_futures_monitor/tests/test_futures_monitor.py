"""Unit tests for BinanceFuturesMonitor."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import os

from crypto_futures_monitor.futures_monitor import BinanceFuturesMonitor, SymbolState


class TestSymbolState(unittest.TestCase):
    """Test cases for SymbolState."""

    def test_add_oi(self):
        """Test adding open interest values."""
        state = SymbolState()
        state.add_oi(100.0)
        state.add_oi(200.0)
        state.add_oi(300.0)
        
        self.assertEqual(len(state.oi_history), 3)
        self.assertEqual(state.oi_history[-1], 300.0)

    def test_add_oi_max_length(self):
        """Test max length constraint on OI history."""
        state = SymbolState()
        for i in range(15):
            state.add_oi(float(i), max_len=10)
        
        self.assertEqual(len(state.oi_history), 10)
        self.assertEqual(state.oi_history[0], 5.0)  # First 5 should be dropped

    def test_get_last_n_mean(self):
        """Test calculating mean of last n values."""
        state = SymbolState()
        state.oi_history = [100.0, 200.0, 300.0, 400.0, 500.0]
        
        mean = state.get_last_n_mean(3)
        self.assertAlmostEqual(mean, 400.0)  # (300 + 400 + 500) / 3

    def test_get_last_n_mean_insufficient_data(self):
        """Test mean calculation with insufficient data."""
        state = SymbolState()
        state.oi_history = [100.0, 200.0]
        
        mean = state.get_last_n_mean(5)
        self.assertIsNone(mean)


class TestBinanceFuturesMonitor(unittest.TestCase):
    """Test cases for BinanceFuturesMonitor."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    def test_init(self, mock_get_env, mock_load_env):
        """Test monitor initialization."""
        mock_get_env.side_effect = lambda k: {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_CHAT_ID': '123456'
        }.get(k)
        
        monitor = BinanceFuturesMonitor()
        
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor.symbol_states, dict)
        self.assertEqual(monitor.telegram_token, 'test_token')
        self.assertEqual(monitor.telegram_chat_id, '123456')

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    @patch('crypto_futures_monitor.futures_monitor.requests.Session')
    def test_get_usdt_perpetual_symbols(self, mock_session, mock_get_env, mock_load_env):
        """Test fetching USDT perpetual symbols."""
        mock_get_env.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbols': [
                {
                    'symbol': 'BTCUSDT',
                    'contractType': 'PERPETUAL',
                    'quoteAsset': 'USDT',
                    'status': 'TRADING'
                },
                {
                    'symbol': 'ETHUSDT',
                    'contractType': 'PERPETUAL',
                    'quoteAsset': 'USDT',
                    'status': 'TRADING'
                },
                {
                    'symbol': 'BNBBTC',
                    'contractType': 'PERPETUAL',
                    'quoteAsset': 'BTC',
                    'status': 'TRADING'
                }
            ]
        }
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        monitor = BinanceFuturesMonitor()
        symbols = monitor.get_usdt_perpetual_symbols()
        
        self.assertEqual(len(symbols), 2)
        self.assertIn('BTCUSDT', symbols)
        self.assertIn('ETHUSDT', symbols)
        self.assertNotIn('BNBBTC', symbols)

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    @patch('crypto_futures_monitor.futures_monitor.requests.Session')
    def test_fetch_premium_index(self, mock_session, mock_get_env, mock_load_env):
        """Test fetching premium index data."""
        mock_get_env.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'BTCUSDT',
            'markPrice': '50000.0',
            'indexPrice': '49950.0',
            'lastFundingRate': '0.0001'
        }
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        monitor = BinanceFuturesMonitor()
        data = monitor.fetch_premium_index('BTCUSDT')
        
        self.assertIsNotNone(data)
        self.assertEqual(data['symbol'], 'BTCUSDT')
        self.assertEqual(data['markPrice'], '50000.0')

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    @patch('crypto_futures_monitor.futures_monitor.requests.Session')
    def test_fetch_open_interest(self, mock_session, mock_get_env, mock_load_env):
        """Test fetching open interest."""
        mock_get_env.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'BTCUSDT',
            'openInterest': '123456.789'
        }
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        monitor = BinanceFuturesMonitor()
        oi = monitor.fetch_open_interest('BTCUSDT')
        
        self.assertAlmostEqual(oi, 123456.789)

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    @patch('crypto_futures_monitor.futures_monitor.requests.Session')
    def test_fetch_ratio_series(self, mock_session, mock_get_env, mock_load_env):
        """Test fetching ratio series data."""
        mock_get_env.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'symbol': 'BTCUSDT',
                'longShortRatio': '1.25',
                'timestamp': 1234567890000
            }
        ]
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        monitor = BinanceFuturesMonitor()
        ratio = monitor._fetch_ratio_series('globalLongShortAccountRatio', 'BTCUSDT', 'longShortRatio')
        
        self.assertAlmostEqual(ratio, 1.25)

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    def test_append_snapshot_to_csv(self, mock_get_env, mock_load_env):
        """Test appending snapshot to CSV."""
        mock_get_env.return_value = None
        
        monitor = BinanceFuturesMonitor()
        # Override DATA_DIR
        import crypto_futures_monitor.futures_monitor as fm
        original_data_dir = fm.DATA_DIR
        fm.DATA_DIR = self.temp_dir
        
        row = {
            'timestamp': '2024-01-01T00:00:00Z',
            'mark_price': 50000.0,
            'oi': 100000.0
        }
        
        monitor.append_snapshot_to_csv('BTCUSDT', row)
        
        csv_file = Path(self.temp_dir) / 'BTCUSDT.csv'
        self.assertTrue(csv_file.exists())
        
        # Restore original
        fm.DATA_DIR = original_data_dir

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    @patch('crypto_futures_monitor.futures_monitor.requests.post')
    def test_send_telegram_alert(self, mock_post, mock_get_env, mock_load_env):
        """Test sending Telegram alert."""
        mock_get_env.side_effect = lambda k: {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_CHAT_ID': '123456'
        }.get(k)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        monitor = BinanceFuturesMonitor()
        monitor.send_telegram_alert('Test alert')
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('test_token', call_args[0][0])

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    def test_check_and_alert_no_alert(self, mock_get_env, mock_load_env):
        """Test check_and_alert when conditions not met."""
        mock_get_env.return_value = None
        
        monitor = BinanceFuturesMonitor()
        state = SymbolState()
        state.oi_history = [100.0] * 10
        
        # Low funding rate - no alert
        monitor.check_and_alert('BTCUSDT', 0.0005, state)
        # No exception means success

    @patch('crypto_futures_monitor.futures_monitor.load_environment_variables')
    @patch('crypto_futures_monitor.futures_monitor.get_env_variable')
    def test_check_and_alert_with_alert(self, mock_get_env, mock_load_env):
        """Test check_and_alert when alert should trigger."""
        mock_get_env.side_effect = lambda k: {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_CHAT_ID': '123456'
        }.get(k)
        
        monitor = BinanceFuturesMonitor()
        state = SymbolState()
        # OI surge: last 3 much higher than last 10
        state.oi_history = [100.0] * 7 + [300.0, 350.0, 400.0]
        
        with patch.object(monitor, 'send_telegram_alert') as mock_alert:
            monitor.check_and_alert('BTCUSDT', 0.002, state)  # High funding rate
            mock_alert.assert_called_once()


if __name__ == '__main__':
    unittest.main()
