"""Binance USDT perpetual futures monitor with Telegram alerts.

This script:
- Fetches key metrics for all USDT-margined perpetual contracts on Binance Futures.
- Runs every 5 minutes in a loop.
- Appends a snapshot per symbol to data/{symbol}.csv.
- Sends Telegram alerts when funding + open interest conditions are met.

Environment variables required:
- TELEGRAM_BOT_TOKEN: Telegram bot token.
- TELEGRAM_CHAT_ID: Target chat ID to receive alerts.
"""
import csv
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests
from loguru import logger

# Add parent directory to path to import utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.utils.env_loader import get_env_variable, load_environment_variables


BINANCE_FAPI_BASE = "https://fapi.binance.com"
SNAPSHOT_INTERVAL_SECONDS = 300  # 5 minutes
RATIO_PERIOD = "5m"  # Align with 5-minute snapshots
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@dataclass
class SymbolState:
    """Keeps recent open interest history for a symbol."""

    oi_history: List[float] = field(default_factory=list)

    def add_oi(self, oi: float, max_len: int = 10) -> None:
        self.oi_history.append(oi)
        if len(self.oi_history) > max_len:
            self.oi_history = self.oi_history[-max_len:]

    def get_last_n_mean(self, n: int) -> Optional[float]:
        if len(self.oi_history) < n:
            return None
        subset = self.oi_history[-n:]
        return sum(subset) / len(subset) if subset else None


class BinanceFuturesMonitor:
    def __init__(self) -> None:
        load_environment_variables()
        self.session = requests.Session()
        self.symbol_states: Dict[str, SymbolState] = {}

        os.makedirs(DATA_DIR, exist_ok=True)

        self.telegram_token = get_env_variable("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = get_env_variable("TELEGRAM_CHAT_ID")
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning(
                "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set; alerts will be disabled."
            )

    # ------------------------------------------------------------------
    # Binance API helpers
    # ------------------------------------------------------------------
    def get_usdt_perpetual_symbols(self) -> List[str]:
        """Fetch all USDT-margined perpetual contract symbols from Binance Futures."""
        url = f"{BINANCE_FAPI_BASE}/fapi/v1/exchangeInfo"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            symbols = []
            for s in data.get("symbols", []):
                if (
                    s.get("contractType") == "PERPETUAL"
                    and s.get("quoteAsset") == "USDT"
                    and s.get("status") == "TRADING"
                ):
                    symbols.append(s["symbol"])
            logger.info(f"Fetched {len(symbols)} USDT perpetual symbols")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch exchangeInfo: {e}")
            return []

    def fetch_premium_index(self, symbol: str) -> Optional[dict]:
        """Get mark price, index price, and last funding rate."""
        url = f"{BINANCE_FAPI_BASE}/fapi/v1/premiumIndex"
        try:
            resp = self.session.get(url, params={"symbol": symbol}, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch premiumIndex for {symbol}: {e}")
            return None

    def fetch_open_interest(self, symbol: str) -> Optional[float]:
        url = f"{BINANCE_FAPI_BASE}/fapi/v1/openInterest"
        try:
            resp = self.session.get(url, params={"symbol": symbol}, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return float(data.get("openInterest"))
        except Exception as e:
            logger.error(f"Failed to fetch openInterest for {symbol}: {e}")
            return None

    def _fetch_ratio_series(self, endpoint: str, symbol: str, value_key: str) -> Optional[float]:
        """Generic helper for futures data ratio endpoints.

        endpoint: e.g. "globalLongShortAccountRatio".
        value_key: key in each list element, e.g. "longShortRatio" or "buySellRatio".
        """
        url = f"{BINANCE_FAPI_BASE}/futures/data/{endpoint}"
        params = {"symbol": symbol, "period": RATIO_PERIOD, "limit": 1}
        try:
            resp = self.session.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                val = data[-1].get(value_key)
                return float(val) if val is not None else None
        except Exception as e:
            logger.error(f"Failed to fetch {endpoint} for {symbol}: {e}")
        return None

    def fetch_long_short_account_ratio(self, symbol: str) -> Optional[float]:
        return self._fetch_ratio_series("globalLongShortAccountRatio", symbol, "longShortRatio")

    def fetch_top_trader_account_ls_ratio(self, symbol: str) -> Optional[float]:
        return self._fetch_ratio_series("topLongShortAccountRatio", symbol, "longShortRatio")

    def fetch_top_trader_position_ls_ratio(self, symbol: str) -> Optional[float]:
        return self._fetch_ratio_series("topLongShortPositionRatio", symbol, "longShortRatio")

    def fetch_taker_buy_sell_ratio(self, symbol: str) -> Optional[float]:
        # takerlongshortRatio endpoint uses buySellRatio field
        return self._fetch_ratio_series("takerlongshortRatio", symbol, "buySellRatio")

    # ------------------------------------------------------------------
    # CSV persistence
    # ------------------------------------------------------------------
    def append_snapshot_to_csv(self, symbol: str, row: Dict[str, float]) -> None:
        filepath = os.path.join(DATA_DIR, f"{symbol}.csv")
        file_exists = os.path.isfile(filepath)

        fieldnames = list(row.keys())
        try:
            with open(filepath, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            logger.error(f"Failed to write CSV for {symbol}: {e}")

    # ------------------------------------------------------------------
    # Telegram alerts
    # ------------------------------------------------------------------
    def send_telegram_alert(self, message: str) -> None:
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured; skipping alert")
            return

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Telegram alert sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    # ------------------------------------------------------------------
    # Main monitoring logic
    # ------------------------------------------------------------------
    def process_symbol(self, symbol: str) -> None:
        """Fetch metrics for a symbol, persist, and maybe trigger alert."""
        premium = self.fetch_premium_index(symbol)
        if not premium:
            return

        try:
            mark_price = float(premium.get("markPrice"))
            index_price = float(premium.get("indexPrice"))
            last_funding_rate = float(premium.get("lastFundingRate"))
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid premiumIndex data for {symbol}: {e}")
            return

        basis = mark_price - index_price
        basis_percent = basis / index_price if index_price else 0.0

        oi = self.fetch_open_interest(symbol)
        if oi is None:
            return

        long_short_account_ratio = self.fetch_long_short_account_ratio(symbol)
        top_trader_account_ls_ratio = self.fetch_top_trader_account_ls_ratio(symbol)
        top_trader_position_ls_ratio = self.fetch_top_trader_position_ls_ratio(symbol)
        taker_buy_sell_ratio = self.fetch_taker_buy_sell_ratio(symbol)

        # Update state for OI history
        state = self.symbol_states.setdefault(symbol, SymbolState())
        state.add_oi(oi)

        # Build snapshot row
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "timestamp": now,
            "mark_price": mark_price,
            "index_price": index_price,
            "basis": basis,
            "basis_percent": basis_percent,
            "last_funding_rate": last_funding_rate,
            "oi": oi,
            "long_short_account_ratio": long_short_account_ratio if long_short_account_ratio is not None else "",
            "top_trader_account_ls_ratio": top_trader_account_ls_ratio if top_trader_account_ls_ratio is not None else "",
            "top_trader_position_ls_ratio": top_trader_position_ls_ratio if top_trader_position_ls_ratio is not None else "",
            "taker_buy_sell_ratio": taker_buy_sell_ratio if taker_buy_sell_ratio is not None else "",
        }

        self.append_snapshot_to_csv(symbol, row)

        # Alert logic
        self.check_and_alert(symbol, last_funding_rate, state)

    def check_and_alert(
        self, symbol: str, last_funding_rate: float, state: SymbolState
    ) -> None:
        """Apply alert logic based on funding and OI history.

        Conditions:
        - abs(last_funding_rate) > 0.001 (0.1%)
        - mean(oi_last_3) / mean(oi_last_10) > 2
        """
        if abs(last_funding_rate) <= 0.001:
            return

        mean_last_3 = state.get_last_n_mean(3)
        mean_last_10 = state.get_last_n_mean(10)

        if mean_last_3 is None or mean_last_10 is None or mean_last_10 == 0:
            # Not enough history yet
            return

        ratio = (mean_last_3 / mean_last_10) if mean_last_10 else 0.0
        if ratio <= 2.0:
            return

        direction = "多头" if last_funding_rate > 0 else "空头"
        message = (
            f"⚠️ *潜在轧空信号*\n"
            f"Symbol: `{symbol}`\n"
            f"Funding rate: `{last_funding_rate:.4%}` ({direction}偏置)\n"
            f"OI(近3次均值) / OI(近10次均值): `{ratio:.2f}` (> 2)\n"
            f"当前时间(UTC): `{datetime.now(timezone.utc).isoformat()}`"
        )
        logger.info(f"Triggering alert for {symbol}: funding={last_funding_rate}, ratio={ratio:.2f}")
        self.send_telegram_alert(message)

    def run(self) -> None:
        """Main loop: fetch symbols and process them every 5 minutes."""
        logger.info("Starting Binance USDT perpetual futures monitor")
        while True:
            start = time.time()
            symbols = self.get_usdt_perpetual_symbols()
            for symbol in symbols:
                try:
                    self.process_symbol(symbol)
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")

            elapsed = time.time() - start
            sleep_for = max(0, SNAPSHOT_INTERVAL_SECONDS - elapsed)
            logger.info(f"Cycle completed in {elapsed:.1f}s, sleeping {sleep_for:.1f}s")
            time.sleep(sleep_for)


def main() -> None:
    monitor = BinanceFuturesMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")


if __name__ == "__main__":
    main()
