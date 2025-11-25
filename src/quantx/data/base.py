"""
Base classes and interfaces for data layer

Defines abstract interfaces for data providers and storage backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, List, Optional

import pandas as pd
from loguru import logger


@dataclass
class MarketData:
    """Standardized market data format"""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate market data"""
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) cannot be less than low ({self.low})")
        if self.high < self.open or self.high < self.close:
            raise ValueError(f"High ({self.high}) must be >= open and close")
        if self.low > self.open or self.low > self.close:
            raise ValueError(f"Low ({self.low}) must be <= open and close")
        if self.volume < 0:
            raise ValueError(f"Volume cannot be negative: {self.volume}")

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "adj_close": self.adj_close,
        }


class IDataProvider(ABC):
    """
    Interface for data providers

    Data providers fetch market data from external sources.
    """

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            interval: Data interval (1m, 5m, 1h, 1d, etc.)

        Returns:
            DataFrame with OHLCV data
        """
        pass

    @abstractmethod
    def get_realtime_data(self, symbols: List[str]) -> Iterator[MarketData]:
        """
        Stream real-time market data

        Args:
            symbols: List of symbols to stream

        Yields:
            MarketData objects
        """
        pass

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if symbol exists

        Args:
            symbol: Symbol to validate

        Returns:
            True if symbol is valid
        """
        pass


class IDataStore(ABC):
    """
    Interface for data storage

    Data stores persist market data for later retrieval.
    """

    @abstractmethod
    def save(self, data: pd.DataFrame, table: str, **kwargs) -> None:
        """
        Save data to storage

        Args:
            data: DataFrame to save
            table: Table/collection name
            **kwargs: Additional storage-specific parameters
        """
        pass

    @abstractmethod
    def load(
        self,
        table: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbols: Optional[List[str]] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load data from storage

        Args:
            table: Table/collection name
            start_date: Optional start date filter
            end_date: Optional end date filter
            symbols: Optional symbol filter
            **kwargs: Additional storage-specific parameters

        Returns:
            DataFrame with requested data
        """
        pass

    @abstractmethod
    def exists(self, table: str) -> bool:
        """
        Check if table exists

        Args:
            table: Table name

        Returns:
            True if table exists
        """
        pass

    @abstractmethod
    def delete(self, table: str, **kwargs) -> None:
        """
        Delete data from storage

        Args:
            table: Table name
            **kwargs: Additional deletion criteria
        """
        pass


def validate_ohlcv_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate OHLCV DataFrame format

    Args:
        df: DataFrame to validate

    Returns:
        True if valid

    Raises:
        ValueError: If DataFrame is invalid
    """
    required_columns = ["open", "high", "low", "close", "volume"]

    # Check required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Check for NaN values
    if df[required_columns].isnull().any().any():
        logger.warning("DataFrame contains NaN values")

    # Validate OHLC relationships
    invalid_high = df["high"] < df[["open", "close", "low"]].max(axis=1)
    if invalid_high.any():
        raise ValueError("High price must be >= open, close, and low")

    invalid_low = df["low"] > df[["open", "close", "high"]].min(axis=1)
    if invalid_low.any():
        raise ValueError("Low price must be <= open, close, and high")

    # Check for negative volume
    if (df["volume"] < 0).any():
        raise ValueError("Volume cannot be negative")

    logger.debug("DataFrame validation passed")
    return True
