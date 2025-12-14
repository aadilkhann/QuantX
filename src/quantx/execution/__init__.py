"""
Execution Module.

Handles live and paper trading execution, order management, and broker integrations.
"""

from quantx.execution.brokers import (
    IBroker,
    BrokerFactory,
    Order,
    Fill,
    Position,
    Account,
    OrderType,
    OrderSide,
    OrderStatus,
    PaperBroker
)

__all__ = [
    # Broker interface
    "IBroker",
    "BrokerFactory",
    
    # Data models
    "Order",
    "Fill",
    "Position",
    "Account",
    
    # Enums
    "OrderType",
    "OrderSide",
    "OrderStatus",
    
    # Implementations
    "PaperBroker",
]
