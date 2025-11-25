"""
Yahoo Finance Data Provider

Provides historical and real-time market data using yfinance library.
"""

from datetime import datetime, timedelta
from typing import Iterator, List, Optional

import pandas as pd
import yfinance as yf
from loguru import logger

from quantx.data.base import IDataProvider, MarketData, validate_ohlcv_dataframe


class YahooFinanceProvider(IDataProvider):
    """
    Yahoo Finance data provider

    Fetches market data from Yahoo Finance using yfinance library.
    Free to use with no API key required.
    """

    def __init__(self, cache_enabled: bool = True) -> None:
        """
        Initialize Yahoo Finance provider

        Args:
            cache_enabled: Whether to enable caching
        """
        self.cache_enabled = cache_enabled
        self._cache: dict = {}
        logger.info("YahooFinanceProvider initialized (cache_enabled={})", cache_enabled)

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Yahoo Finance

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            start_date: Start date
            end_date: End date
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with columns: open, high, low, close, volume, adj_close

        Raises:
            ValueError: If symbol is invalid or data fetch fails
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"

        # Check cache
        if self.cache_enabled and cache_key in self._cache:
            logger.debug("Returning cached data for {}", symbol)
            return self._cache[cache_key].copy()

        logger.info(
            "Fetching historical data for {} from {} to {} (interval: {})",
            symbol,
            start_date.date(),
            end_date.date(),
            interval,
        )

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)

            if df.empty:
                raise ValueError(f"No data returned for symbol: {symbol}")

            # Standardize column names
            df = df.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )

            # Add adjusted close if available
            if "Adj Close" in df.columns:
                df["adj_close"] = df["Adj Close"]
                df = df.drop(columns=["Adj Close"])
            else:
                df["adj_close"] = df["close"]

            # Remove dividends and stock splits columns if present
            df = df[["open", "high", "low", "close", "volume", "adj_close"]]

            # Validate data
            validate_ohlcv_dataframe(df)

            # Cache result
            if self.cache_enabled:
                self._cache[cache_key] = df.copy()

            logger.info("Fetched {} rows for {}", len(df), symbol)
            return df

        except Exception as e:
            logger.error("Failed to fetch data for {}: {}", symbol, e)
            raise ValueError(f"Failed to fetch data for {symbol}: {e}")

    def get_realtime_data(self, symbols: List[str]) -> Iterator[MarketData]:
        """
        Stream real-time market data

        Note: Yahoo Finance doesn't provide true real-time streaming.
        This method polls for latest data at regular intervals.

        Args:
            symbols: List of symbols to stream

        Yields:
            MarketData objects
        """
        logger.warning("Yahoo Finance does not support true real-time streaming")
        logger.info("Polling for latest data for {} symbols", len(symbols))

        while True:
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    # Get last 2 days to ensure we have latest data
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=2)

                    df = ticker.history(start=start_date, end=end_date, interval="1m")

                    if not df.empty:
                        # Get latest row
                        latest = df.iloc[-1]
                        market_data = MarketData(
                            symbol=symbol,
                            timestamp=latest.name.to_pydatetime(),
                            open=float(latest["Open"]),
                            high=float(latest["High"]),
                            low=float(latest["Low"]),
                            close=float(latest["Close"]),
                            volume=int(latest["Volume"]),
                            adj_close=float(latest.get("Adj Close", latest["Close"])),
                        )
                        yield market_data

                except Exception as e:
                    logger.error("Error fetching real-time data for {}: {}", symbol, e)

            # Wait before next poll (avoid rate limiting)
            import time

            time.sleep(60)  # Poll every minute

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if symbol exists on Yahoo Finance

        Args:
            symbol: Symbol to validate

        Returns:
            True if symbol is valid
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Check if we got valid info
            if not info or "regularMarketPrice" not in info:
                logger.warning("Symbol {} not found or invalid", symbol)
                return False

            logger.debug("Symbol {} is valid", symbol)
            return True

        except Exception as e:
            logger.error("Error validating symbol {}: {}", symbol, e)
            return False

    def get_symbol_info(self, symbol: str) -> dict:
        """
        Get detailed information about a symbol

        Args:
            symbol: Symbol to get info for

        Returns:
            Dictionary with symbol information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "name": info.get("longName", ""),
                "exchange": info.get("exchange", ""),
                "currency": info.get("currency", ""),
                "market_cap": info.get("marketCap", 0),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
            }

        except Exception as e:
            logger.error("Error getting info for {}: {}", symbol, e)
            return {"symbol": symbol, "error": str(e)}

    def clear_cache(self) -> None:
        """Clear the data cache"""
        self._cache.clear()
        logger.info("Cache cleared")
