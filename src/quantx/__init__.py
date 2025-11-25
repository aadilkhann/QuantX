"""
QuantX - AI-Powered & Rule-Based Trading System

A modular algorithmic trading platform that combines AI/ML models with
rule-based strategies for fast, efficient, and reliable trading.
"""

__version__ = "0.1.0"
__author__ = "QuantX Team"
__license__ = "MIT"

from quantx.core.events import Event, EventBus, EventType
from quantx.core.config import Config

__all__ = [
    "__version__",
    "Event",
    "EventBus",
    "EventType",
    "Config",
]
