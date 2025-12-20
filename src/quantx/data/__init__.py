"""
Data Module for QuantX.

Provides data providers, streaming, and instrument management.
"""

from quantx.data.providers.base import IDataProvider
from quantx.data.providers.yahoo import YahooFinanceProvider
from quantx.data.streaming import ZerodhaWebSocket, LiveDataProvider
from quantx.data.instruments import InstrumentManager

__all__ = [
    "IDataProvider",
    "YahooFinanceProvider",
    "ZerodhaWebSocket",
    "LiveDataProvider",
    "InstrumentManager",
]
