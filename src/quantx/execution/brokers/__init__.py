"""
Execution Brokers Module.

Provides broker integrations for live and paper trading.
"""

from quantx.execution.brokers.base import (
    IBroker,
    Order,
    Fill,
    Position,
    Account,
    OrderType,
    OrderSide,
    OrderStatus,
    BrokerFactory,
    BrokerConnection
)

from quantx.execution.brokers.paper_broker import PaperBroker

__all__ = [
    # Base classes
    "IBroker",
    "BrokerFactory",
    "BrokerConnection",
    
    # Data models
    "Order",
    "Fill",
    "Position",
    "Account",
    
    # Enums
    "OrderType",
    "OrderSide",
    "OrderStatus",
    
    # Broker implementations
    "PaperBroker",
]
