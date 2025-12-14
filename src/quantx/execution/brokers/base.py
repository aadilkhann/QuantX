"""
Broker Base Classes and Interfaces.

This module defines the abstract interfaces that all broker implementations
must follow, ensuring consistent behavior across different brokers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import pandas as pd
from loguru import logger


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status enumeration."""
    CREATED = "created"
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class Order:
    """
    Order data model.
    
    Represents a trading order with all necessary information.
    """
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None  # For limit orders
    stop_price: Optional[float] = None  # For stop orders
    status: OrderStatus = OrderStatus.CREATED
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    created_at: datetime = None
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_open(self) -> bool:
        """Check if order is still open."""
        return self.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED]
    
    @property
    def remaining_quantity(self) -> float:
        """Get remaining unfilled quantity."""
        return self.quantity - self.filled_quantity


@dataclass
class Fill:
    """
    Fill/execution data model.
    
    Represents a partial or complete fill of an order.
    """
    fill_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    commission: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def total_cost(self) -> float:
        """Get total cost including commission."""
        return (self.quantity * self.price) + self.commission


@dataclass
class Position:
    """
    Position data model.
    
    Represents a current position in a symbol.
    """
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    
    @property
    def cost_basis(self) -> float:
        """Get total cost basis."""
        return self.quantity * self.average_price


@dataclass
class Account:
    """
    Account data model.
    
    Represents broker account information.
    """
    account_id: str
    cash: float
    equity: float
    buying_power: float
    positions_value: float
    unrealized_pnl: float
    realized_pnl: float
    initial_capital: float
    
    @property
    def total_pnl(self) -> float:
        """Get total P&L."""
        return self.unrealized_pnl + self.realized_pnl
    
    @property
    def return_pct(self) -> float:
        """Get return percentage."""
        if self.initial_capital == 0:
            return 0.0
        return (self.equity - self.initial_capital) / self.initial_capital * 100


class BrokerConnection:
    """
    Broker connection management.
    
    Handles connection state, authentication, and reconnection logic.
    """
    
    def __init__(self, broker_name: str):
        """
        Initialize connection manager.
        
        Args:
            broker_name: Name of the broker
        """
        self.broker_name = broker_name
        self.connected = False
        self.authenticated = False
        self.last_heartbeat: Optional[datetime] = None
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected
    
    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self.authenticated


class IBroker(ABC):
    """
    Abstract broker interface.
    
    All broker implementations must inherit from this class and implement
    all abstract methods.
    
    Example:
        >>> class MyBroker(IBroker):
        ...     def connect(self):
        ...         # Implementation
        ...         pass
        ...     
        ...     def place_order(self, order):
        ...         # Implementation
        ...         pass
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize broker.
        
        Args:
            name: Broker name
            config: Broker configuration
        """
        self.name = name
        self.config = config
        self.connection = BrokerConnection(name)
        logger.info(f"Initialized {name} broker")
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to broker.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from broker.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check connection status.
        
        Returns:
            True if connected
        """
        pass
    
    @abstractmethod
    def place_order(self, order: Order) -> str:
        """
        Place an order.
        
        Args:
            order: Order to place
            
        Returns:
            Order ID assigned by broker
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancellation successful
        """
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get order details.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order object or None if not found
        """
        pass
    
    @abstractmethod
    def get_open_orders(self) -> List[Order]:
        """
        Get all open orders.
        
        Returns:
            List of open orders
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """
        Get all current positions.
        
        Returns:
            List of positions
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a specific symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position object or None if no position
        """
        pass
    
    @abstractmethod
    def get_account(self) -> Account:
        """
        Get account information.
        
        Returns:
            Account object
        """
        pass
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, float]:
        """
        Get current quote for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with bid, ask, last price
        """
        pass
    
    def validate_order(self, order: Order) -> bool:
        """
        Validate order before submission.
        
        Args:
            order: Order to validate
            
        Returns:
            True if valid
        """
        # Basic validation
        if order.quantity <= 0:
            logger.error(f"Invalid quantity: {order.quantity}")
            return False
        
        if order.order_type == OrderType.LIMIT and order.price is None:
            logger.error("Limit order requires price")
            return False
        
        if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and order.stop_price is None:
            logger.error("Stop order requires stop price")
            return False
        
        return True


class BrokerFactory:
    """
    Factory for creating broker instances.
    
    Example:
        >>> factory = BrokerFactory()
        >>> factory.register("paper", PaperBroker)
        >>> broker = factory.create("paper", config)
    """
    
    _brokers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, broker_class: type):
        """
        Register a broker implementation.
        
        Args:
            name: Broker name
            broker_class: Broker class
        """
        cls._brokers[name] = broker_class
        logger.info(f"Registered broker: {name}")
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> IBroker:
        """
        Create a broker instance.
        
        Args:
            name: Broker name
            config: Broker configuration
            
        Returns:
            Broker instance
        """
        if name not in cls._brokers:
            raise ValueError(f"Unknown broker: {name}. Available: {list(cls._brokers.keys())}")
        
        broker_class = cls._brokers[name]
        return broker_class(name, config)
    
    @classmethod
    def list_brokers(cls) -> List[str]:
        """
        List available brokers.
        
        Returns:
            List of broker names
        """
        return list(cls._brokers.keys())
