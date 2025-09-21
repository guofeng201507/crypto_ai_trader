"""
Unit tests for the discrepancy detection functionality
"""
import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import detect_discrepancies, calculate_weighted_price


class TestDiscrepancyDetection(unittest.TestCase):
    """Test cases for the discrepancy detection functions"""
    
    def test_calculate_weighted_price_simple(self):
        """Test calculating weighted price with simple orderbook"""
        # Simple orderbook: [price, volume]
        orders = [
            [100.0, 1.0],  # 1 unit at 100
            [101.0, 1.0],  # 1 unit at 101
            [102.0, 1.0]   # 1 unit at 102
        ]
        
        # Test filling exactly 1 unit
        price = calculate_weighted_price(orders, 1.0)
        self.assertEqual(price, 100.0)
        
        # Test filling exactly 2 units
        price = calculate_weighted_price(orders, 2.0)
        self.assertEqual(price, 100.5)  # (100*1 + 101*1) / 2
        
        # Test filling exactly 3 units
        price = calculate_weighted_price(orders, 3.0)
        self.assertEqual(price, 101.0)  # (100*1 + 101*1 + 102*1) / 3
        
        # Test filling partial units
        price = calculate_weighted_price(orders, 1.5)
        self.assertAlmostEqual(price, 100.33333333333333, places=10)  # (100*1 + 101*0.5) / 1.5
    
    def test_calculate_weighted_price_insufficient_liquidity(self):
        """Test calculating weighted price with insufficient liquidity"""
        # Simple orderbook: [price, volume]
        orders = [
            [100.0, 1.0],  # 1 unit at 100
            [101.0, 1.0]   # 1 unit at 101
        ]
        
        # Try to fill more units than available
        price = calculate_weighted_price(orders, 3.0)
        self.assertIsNone(price)
    
    def test_calculate_weighted_price_edge_cases(self):
        """Test calculating weighted price with edge cases"""
        # Empty orderbook
        price = calculate_weighted_price([], 1.0)
        self.assertIsNone(price)
        
        # Zero target volume
        orders = [[100.0, 1.0]]
        price = calculate_weighted_price(orders, 0.0)
        self.assertIsNone(price)
        
        # Negative target volume
        price = calculate_weighted_price(orders, -1.0)
        self.assertIsNone(price)
    
    def test_detect_discrepancies_no_opportunities(self):
        """Test discrepancy detection with no arbitrage opportunities"""
        # Orderbooks with no significant discrepancies
        orderbooks = {
            'binance': {
                'SOL/USDT': {
                    'bids': [[100.0, 1.0]],  # Best bid: 100
                    'asks': [[101.0, 1.0]]   # Best ask: 101
                }
            },
            'okx': {
                'SOL/USDT': {
                    'bids': [[99.5, 1.0]],   # Best bid: 99.5
                    'asks': [[101.5, 1.0]]   # Best ask: 101.5
                }
            }
        }
        
        # Capture print output
        import io
        import contextlib
        
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            detect_discrepancies(orderbooks, 1.0)  # 1% threshold
        
        # Should not detect any opportunities (0.5% discrepancy < 1% threshold)
        output = captured_output.getvalue()
        self.assertEqual(output, "")
    
    def test_detect_discrepancies_with_opportunity(self):
        """Test discrepancy detection with an arbitrage opportunity"""
        # Orderbooks with a clear arbitrage opportunity
        orderbooks = {
            'binance': {
                'SOL/USDT': {
                    'bids': [[102.0, 1.0]],  # Best bid: 102 (sell price)
                    'asks': [[101.0, 1.0]]   # Best ask: 101 (buy price)
                }
            },
            'okx': {
                'SOL/USDT': {
                    'bids': [[99.5, 1.0]],   # Best bid: 99.5 (sell price)
                    'asks': [[100.0, 1.0]]   # Best ask: 100 (buy price)
                }
            }
        }
        
        # There's an opportunity: Buy on OKX at 100, sell on Binance at 102
        # Profit: 2 per unit, which is 2% (2/100 * 100)
        
        # Capture print output
        import io
        import contextlib
        
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            detect_discrepancies(orderbooks, 1.0)  # 1% threshold
        
        # Should detect the opportunity
        output = captured_output.getvalue()
        self.assertIn("ARBITRAGE OPPORTUNITY", output)
        self.assertIn("Buy  on okx at $100.0000", output)
        self.assertIn("Sell on binance at $102.0000", output)


if __name__ == '__main__':
    unittest.main()