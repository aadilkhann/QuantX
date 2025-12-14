"""
Paper Trading Broker.

Simulated broker for risk-free testing and validation before live trading.
Provides realistic order execution simulation with configurable slippage and commissions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import pandas as pd
import numpy as np
from loguru import logger

from quantx.execution.brokers.base import (
    IBroker, Order, Fill, Position, Account,
    OrderType, OrderSide, OrderStatus
)


class PaperBroker(IBroker):
    """
    Paper trading broker with simulated execution.
    
    Features:
    - Realistic order execution simulation
    - Configurable slippage and commissions
    - Market impact modeling
    - Portfolio tracking
    - Trade history
    
    Example:
        >>> broker = PaperBroker(
        ...     name="paper",
        ...     config={
        ...         "initial_capital": 100000,
        ...         "commission": 0.001,  # 0.1%
        ...         "slippage": 0.0005    # 0.05%
        ...     }
        ... )
        >>> broker.connect()
        >>> order = Order(...)
        >>> order_id = broker.place_order(order)
    """
    
    def __init__(self, name: str = "paper", config: Optional[Dict[str, Any]] = None):
        """
        Initialize paper broker.
        
        Args:
            name: Broker name
            config: Configuration dictionary
        """
        if config is None:
            config = {}
        
        super().__init__(name, config)
        
        # Configuration
        self.initial_capital = config.get("initial_capital", 100000.0)
        self.commission_rate = config.get("commission", 0.001)  # 0.1%
        self.slippage_rate = config.get("slippage", 0.0005)  # 0.05%
        self.market_impact_rate = config.get("market_impact", 0.0001)  # 0.01%
        
        # State
        self.cash = self.initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.fills: List[Fill] = []
        self.trade_history: List[Dict[str, Any]] = []
        
        # Market data (for simulation)
        self.current_prices: Dict[str, float] = {}
        
        logger.info(f"Initialized paper broker with ${self.initial_capital:,.2f}")
    
    def connect(self) -> bool:
        """Connect to paper broker (always succeeds)."""
        self.connection.connected = True
        self.connection.authenticated = True
        logger.info("Connected to paper broker")
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from paper broker."""
        self.connection.connected = False
        self.connection.authenticated = False
        logger.info("Disconnected from paper broker")
        return True
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connection.connected
    
    def place_order(self, order: Order) -> str:
        """
        Place an order in paper trading.
        
        Args:
            order: Order to place
            
        Returns:
            Order ID
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to broker")
        
        # Validate order
        if not self.validate_order(order):
            order.status = OrderStatus.REJECTED
            logger.error(f"Order validation failed: {order}")
            return order.order_id
        
        # Generate order ID if not provided
        if not order.order_id:
            order.order_id = f"paper_{uuid.uuid4().hex[:8]}"
        
        # Update order status
        order.status = OrderStatus.SUBMITTED
        order.submitted_at = datetime.now()
        
        # Store order
        self.orders[order.order_id] = order
        
        # Simulate immediate execution for market orders
        if order.order_type == OrderType.MARKET:
            self._execute_market_order(order)
        else:
            # For limit/stop orders, mark as pending
            order.status = OrderStatus.PENDING
        
        logger.info(f"Placed order: {order.order_id} - {order.side.value} {order.quantity} {order.symbol}")
        
        return order.order_id
    
    def _execute_market_order(self, order: Order):
        """
        Execute a market order immediately.
        
        Args:
            order: Market order to execute
        """
        # Get current price
        if order.symbol not in self.current_prices:
            logger.error(f"No price data for {order.symbol}")
            order.status = OrderStatus.REJECTED
            return
        
        current_price = self.current_prices[order.symbol]
        
        # Calculate fill price with slippage
        fill_price = self._calculate_fill_price(current_price, order.side, order.quantity)
        
        # Calculate commission
        commission = self._calculate_commission(order.quantity, fill_price)
        
        # Check if we have enough cash (for buy orders)
        if order.side == OrderSide.BUY:
            total_cost = (order.quantity * fill_price) + commission
            if total_cost > self.cash:
                logger.error(f"Insufficient funds: need ${total_cost:,.2f}, have ${self.cash:,.2f}")
                order.status = OrderStatus.REJECTED
                return
        
        # Create fill
        fill = Fill(
            fill_id=f"fill_{uuid.uuid4().hex[:8]}",
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            timestamp=datetime.now()
        )
        
        # Process fill
        self._process_fill(fill, order)
        
        logger.info(
            f"Executed order {order.order_id}: {order.quantity} @ ${fill_price:.2f} "
            f"(commission: ${commission:.2f})"
        )
    
    def _calculate_fill_price(self, current_price: float, side: OrderSide, quantity: float) -> float:
        """
        Calculate fill price with slippage and market impact.
        
        Args:
            current_price: Current market price
            side: Order side
            quantity: Order quantity
            
        Returns:
            Fill price
        """
        # Base slippage
        slippage = current_price * self.slippage_rate
        
        # Market impact (increases with quantity)
        market_impact = current_price * self.market_impact_rate * np.log(1 + quantity / 100)
        
        # Apply slippage and market impact
        if side == OrderSide.BUY:
            # Buy at higher price (worse for us)
            fill_price = current_price + slippage + market_impact
        else:
            # Sell at lower price (worse for us)
            fill_price = current_price - slippage - market_impact
        
        return fill_price
    
    def _calculate_commission(self, quantity: float, price: float) -> float:
        """
        Calculate commission.
        
        Args:
            quantity: Order quantity
            price: Fill price
            
        Returns:
            Commission amount
        """
        return quantity * price * self.commission_rate
    
    def _process_fill(self, fill: Fill, order: Order):
        """
        Process a fill and update positions.
        
        Args:
            fill: Fill to process
            order: Associated order
        """
        # Store fill
        self.fills.append(fill)
        
        # Update order
        order.filled_quantity += fill.quantity
        order.average_fill_price = (
            (order.average_fill_price * (order.filled_quantity - fill.quantity) +
             fill.price * fill.quantity) / order.filled_quantity
        )
        
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.now()
        else:
            order.status = OrderStatus.PARTIALLY_FILLED
        
        # Update position
        self._update_position(fill)
        
        # Update cash
        if fill.side == OrderSide.BUY:
            self.cash -= fill.total_cost
        else:
            self.cash += (fill.quantity * fill.price) - fill.commission
        
        # Record trade
        self.trade_history.append({
            "timestamp": fill.timestamp,
            "symbol": fill.symbol,
            "side": fill.side.value,
            "quantity": fill.quantity,
            "price": fill.price,
            "commission": fill.commission,
            "order_id": fill.order_id,
            "fill_id": fill.fill_id
        })
    
    def _update_position(self, fill: Fill):
        """
        Update position based on fill.
        
        Args:
            fill: Fill to process
        """
        symbol = fill.symbol
        
        if symbol not in self.positions:
            # New position
            if fill.side == OrderSide.BUY:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=fill.quantity,
                    average_price=fill.price,
                    current_price=fill.price,
                    market_value=fill.quantity * fill.price,
                    unrealized_pnl=0.0
                )
        else:
            # Update existing position
            position = self.positions[symbol]
            
            if fill.side == OrderSide.BUY:
                # Add to position
                total_quantity = position.quantity + fill.quantity
                position.average_price = (
                    (position.average_price * position.quantity + fill.price * fill.quantity) /
                    total_quantity
                )
                position.quantity = total_quantity
            else:
                # Reduce position
                position.quantity -= fill.quantity
                
                # Calculate realized P&L
                realized_pnl = (fill.price - position.average_price) * fill.quantity - fill.commission
                position.realized_pnl += realized_pnl
                
                # Remove position if quantity is zero
                if position.quantity <= 0:
                    del self.positions[symbol]
                    return
            
            # Update market value
            position.current_price = self.current_prices.get(symbol, fill.price)
            position.market_value = position.quantity * position.current_price
            position.unrealized_pnl = (position.current_price - position.average_price) * position.quantity
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful
        """
        if order_id not in self.orders:
            logger.error(f"Order not found: {order_id}")
            return False
        
        order = self.orders[order_id]
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
            logger.error(f"Cannot cancel order in status: {order.status}")
            return False
        
        order.status = OrderStatus.CANCELLED
        logger.info(f"Cancelled order: {order_id}")
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)
    
    def get_open_orders(self) -> List[Order]:
        """Get all open orders."""
        return [
            order for order in self.orders.values()
            if order.is_open
        ]
    
    def get_positions(self) -> List[Position]:
        """Get all positions."""
        return list(self.positions.values())
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for symbol."""
        return self.positions.get(symbol)
    
    def get_account(self) -> Account:
        """Get account information."""
        # Calculate positions value
        positions_value = sum(pos.market_value for pos in self.positions.values())
        
        # Calculate unrealized P&L
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        # Calculate realized P&L
        realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        
        # Total equity
        equity = self.cash + positions_value
        
        return Account(
            account_id="paper_account",
            cash=self.cash,
            equity=equity,
            buying_power=self.cash,  # Simplified: no margin
            positions_value=positions_value,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
            initial_capital=self.initial_capital
        )
    
    def get_quote(self, symbol: str) -> Dict[str, float]:
        """
        Get current quote for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with bid, ask, last price
        """
        if symbol not in self.current_prices:
            return {"bid": 0.0, "ask": 0.0, "last": 0.0}
        
        price = self.current_prices[symbol]
        spread = price * 0.0001  # 0.01% spread
        
        return {
            "bid": price - spread / 2,
            "ask": price + spread / 2,
            "last": price
        }
    
    def update_prices(self, prices: Dict[str, float]):
        """
        Update current market prices.
        
        Args:
            prices: Dictionary of symbol -> price
        """
        self.current_prices.update(prices)
        
        # Update position market values
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.current_price = prices[symbol]
                position.market_value = position.quantity * position.current_price
                position.unrealized_pnl = (
                    (position.current_price - position.average_price) * position.quantity
                )
    
    def get_trade_history(self) -> pd.DataFrame:
        """
        Get trade history as DataFrame.
        
        Returns:
            DataFrame with trade history
        """
        if not self.trade_history:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trade_history)
    
    def reset(self):
        """Reset broker to initial state."""
        self.cash = self.initial_capital
        self.positions.clear()
        self.orders.clear()
        self.fills.clear()
        self.trade_history.clear()
        self.current_prices.clear()
        logger.info("Reset paper broker to initial state")


# Register paper broker with factory
from quantx.execution.brokers.base import BrokerFactory
BrokerFactory.register("paper", PaperBroker)
