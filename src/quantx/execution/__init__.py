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

from quantx.execution.orders import (
    OrderValidator,
    OrderManager,
    MultiOrderManager
)

from quantx.execution.risk import (
    RiskLevel,
    RiskLimits,
    RiskViolation,
    RiskManager
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
    
    # Order Management
    "OrderValidator",
    "OrderManager",
    "MultiOrderManager",
    
    # Risk Management
    "RiskLevel",
    "RiskLimits",
    "RiskViolation",
    "RiskManager",
]
