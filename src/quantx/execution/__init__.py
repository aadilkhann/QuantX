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

# Live Trading Components
from quantx.execution.live_engine import (
    LiveExecutionEngine,
    EngineState,
    EngineConfig
)

from quantx.execution.position_sync import (
    PositionSynchronizer,
    PositionDiscrepancy,
    ReconciliationReport
)

from quantx.execution.live_pnl import (
    LivePnLTracker,
    TradeRecord,
    DailyPnL,
    LivePnLSnapshot
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
    
    # Live Trading
    "LiveExecutionEngine",
    "EngineState",
    "EngineConfig",
    "PositionSynchronizer",
    "PositionDiscrepancy",
    "ReconciliationReport",
    "LivePnLTracker",
    "TradeRecord",
    "DailyPnL",
    "LivePnLSnapshot",
]
