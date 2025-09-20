#!/usr/bin/env python3
"""
Crypto Orderbook Monitor
Monitors orderbooks from multiple exchanges and detects price discrepancies
"""

import asyncio
import yaml
import sys
import os

from src.exchanges.binance import BinanceExchange
from src.exchanges.okx import OkxExchange
from src.exchanges.coinbase import CoinbaseExchange
from src.utils.config_manager import ConfigManager
from loguru import logger


async def main():
    """Main function to run the orderbook monitor"""
    try:
        # Load configuration
        config_manager = ConfigManager('config.yaml')
        config = config_manager.get_config()
        
        # Setup logging
        logger.remove()
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to project root
        project_root = os.path.dirname(current_dir)
        log_file_path = os.path.join(project_root, config['log_file'])
        logger.add(log_file_path, level=config['log_level'], rotation="500 MB")
        logger.add("stderr", level=config['log_level'])
        
        logger.info("Starting Crypto Orderbook Monitor")
        logger.info(f"Monitoring pairs: {config['trading_pairs']}")
        logger.info(f"Refresh rate: {config['refresh_rate']} seconds")
        logger.info(f"Threshold: {config['threshold_percentage']}%")
        
        # Initialize exchanges
        exchanges = []
        exchange_instances = []
        for exchange_config in config['exchanges']:
            if exchange_config['enabled']:
                try:
                    if exchange_config['name'] == 'binance':
                        exchange = BinanceExchange()
                        exchanges.append(exchange)
                        exchange_instances.append(exchange)
                        logger.info(f"Initialized {exchange_config['name']} exchange")
                    elif exchange_config['name'] == 'okx':
                        exchange = OkxExchange()
                        exchanges.append(exchange)
                        exchange_instances.append(exchange)
                        logger.info(f"Initialized {exchange_config['name']} exchange")
                    elif exchange_config['name'] == 'coinbase':
                        exchange = CoinbaseExchange()
                        exchanges.append(exchange)
                        exchange_instances.append(exchange)
                        logger.info(f"Initialized {exchange_config['name']} exchange")
                except Exception as e:
                    logger.error(f"Failed to initialize {exchange_config['name']} exchange: {e}")
        
        if not exchanges:
            logger.error("No exchanges initialized. Exiting.")
            return
        
        # Trading pairs to monitor
        trading_pairs = config['trading_pairs']
        
        # Monitor loop
        iteration = 0
        try:
            while True:
                iteration += 1
                logger.debug(f"Starting iteration {iteration}")
                
                # Fetch orderbooks from all exchanges for all trading pairs
                orderbooks = {}
                for exchange in exchanges:
                    orderbooks[exchange.name] = {}
                    for pair in trading_pairs:
                        try:
                            orderbook = await exchange.fetch_orderbook(pair)
                            orderbooks[exchange.name][pair] = orderbook
                            logger.debug(f"Fetched orderbook for {pair} from {exchange.name}")
                        except Exception as e:
                            logger.error(f"Error fetching orderbook from {exchange.name} for {pair}: {e}")
                
                # Detect price discrepancies
                detect_discrepancies(orderbooks, config['threshold_percentage'])
                
                # Wait before next refresh
                await asyncio.sleep(config['refresh_rate'])
                
        except KeyboardInterrupt:
            logger.info("Shutting down monitor...")
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
        finally:
            # Close exchange connections
            for exchange in exchange_instances:
                try:
                    await exchange.close()
                    logger.info(f"Closed connection to {exchange.name}")
                except Exception as e:
                    logger.error(f"Error closing connection to {exchange.name}: {e}")
                    
    except Exception as e:
        logger.error(f"Fatal error in main function: {e}")
        raise


def detect_discrepancies(orderbooks, threshold_percentage):
    """Detect price discrepancies between exchanges"""
    if not orderbooks:
        return
        
    # Get the first exchange to determine available pairs
    first_exchange = list(orderbooks.keys())[0]
    if not orderbooks[first_exchange]:
        return
        
    # For each trading pair
    for pair in orderbooks[first_exchange].keys():
        # Get best bid and ask from each exchange
        best_bids = {}
        best_asks = {}
        bid_volumes = {}
        ask_volumes = {}
        
        for exchange_name, pairs in orderbooks.items():
            if pair in pairs and pairs[pair]:
                orderbook = pairs[pair]
                if 'bids' in orderbook and len(orderbook['bids']) > 0:
                    best_bids[exchange_name] = orderbook['bids'][0][0]  # Price
                    bid_volumes[exchange_name] = orderbook['bids'][0][1]  # Volume
                if 'asks' in orderbook and len(orderbook['asks']) > 0:
                    best_asks[exchange_name] = orderbook['asks'][0][0]  # Price
                    ask_volumes[exchange_name] = orderbook['asks'][0][1]  # Volume
        
        # Find maximum bid and minimum ask across exchanges
        if best_bids:
            max_bid_exchange = max(best_bids, key=best_bids.get)
            max_bid_price = best_bids[max_bid_exchange]
            max_bid_volume = bid_volumes.get(max_bid_exchange, 0)
        else:
            max_bid_exchange = None
            max_bid_price = 0
            max_bid_volume = 0
            
        if best_asks:
            min_ask_exchange = min(best_asks, key=best_asks.get)
            min_ask_price = best_asks[min_ask_exchange]
            min_ask_volume = ask_volumes.get(min_ask_exchange, 0)
        else:
            min_ask_exchange = None
            min_ask_price = float('inf')
            min_ask_volume = 0
        
        # Calculate discrepancy
        if (max_bid_exchange and min_ask_exchange and 
            max_bid_price > 0 and min_ask_price < float('inf') and
            max_bid_exchange != min_ask_exchange):
            
            discrepancy = max_bid_price - min_ask_price
            discrepancy_percentage = (discrepancy / min_ask_price) * 100
            
            # Alert if discrepancy exceeds threshold
            if discrepancy_percentage >= threshold_percentage:
                # Calculate potential profit (limited by smallest volume)
                tradable_volume = min(max_bid_volume, min_ask_volume)
                potential_profit = discrepancy * tradable_volume
                
                logger.info(f"ARBITRAGE OPPORTUNITY - {pair}:")
                logger.info(f"  Buy  on {min_ask_exchange} at ${min_ask_price:.4f} (vol: {min_ask_volume})")
                logger.info(f"  Sell on {max_bid_exchange} at ${max_bid_price:.4f} (vol: {max_bid_volume})")
                logger.info(f"  Profit: ${discrepancy:.4f} ({discrepancy_percentage:.2f}%)")
                logger.info(f"  Potential profit for {tradable_volume}: ${potential_profit:.4f}")
                
                print(f"ARBITRAGE OPPORTUNITY - {pair}:")
                print(f"  Buy  on {min_ask_exchange} at ${min_ask_price:.4f} (vol: {min_ask_volume})")
                print(f"  Sell on {max_bid_exchange} at ${max_bid_price:.4f} (vol: {max_bid_volume})")
                print(f"  Profit: ${discrepancy:.4f} ({discrepancy_percentage:.2f}%)")
                print(f"  Potential profit for {tradable_volume}: ${potential_profit:.4f}")
                print("-" * 50)