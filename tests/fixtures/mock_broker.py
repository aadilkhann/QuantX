"""
Mock broker for testing.
"""

from typing import Dict, List, Optional
from datetime import datetime
from quantx.execution.brokers.base import IBroker, Order, OrderStatus, Fill


class MockBroker(IBroker):
    """
    Mock broker for testing.
    
    Simulates a broker without making actual API calls.
    """
    
    def __init__(self):
        self.broker_id = "mock_broker"
        self.name = "MockBroker"  # Add name attribute
        self._connected = False
        self._orders: Dict[str, Order] = {}
        self._positions: Dict[str, Dict] = {}
        self._account = {
            "equity": 100000.0,
            "cash": 100000.0,
            "margin_used": 0.0
        }
        self._next_order_id = 1
        
        # For testing
        self.placed_orders = []
        self.cancelled_orders = []
    
    def connect(self) -> bool:
        """Connect to mock broker."""
        self._connected = True
        return True
    
    def disconnect(self):
        """Disconnect from mock broker."""
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected
    
    def place_order(self, order: Order) -> str:
        """Place an order."""
        if not self._connected:
            raise RuntimeError("Broker not connected")
        
        # Generate order ID
        order_id = f"MOCK{self._next_order_id:06d}"
        self._next_order_id += 1
        
        # Store order
        order.order_id = order_id
        order.status = OrderStatus.SUBMITTED
        self._orders[order_id] = order
        self.placed_orders.append(order)
        
        # Auto-fill for testing (simulate immediate fill)
        self._fill_order(order)
        
        return order_id
    
    def _fill_order(self, order: Order):
        """Simulate order fill."""
        fill = Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            quantity=order.quantity,
            price=order.price if order.price else 1000.0,  # Mock price
            side=order.side,
            timestamp=datetime.now(),
            commission=10.0
        )
        
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.fills.append(fill)
        
        # Update positions
        position = self._positions.get(order.symbol, {"quantity": 0, "average_price": 0})
        
        if order.side.value == "BUY":
            new_qty = position["quantity"] + order.quantity
            if new_qty > 0:
                position["average_price"] = (
                    (position["quantity"] * position.get("average_price", 0) + 
                     order.quantity * fill.price) / new_qty
                )
            position["quantity"] = new_qty
        else:  # SELL
            position["quantity"] -= order.quantity
        
        self._positions[order.symbol] = position
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if order_id in self._orders:
            order = self._orders[order_id]
            order.status = OrderStatus.CANCELLED
            self.cancelled_orders.append(order_id)
            return True
        return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self._orders.get(order_id)
    
    def get_open_orders(self) -> List[Order]:
        """Get all open orders."""
        return [
            order for order in self._orders.values()
            if order.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]
        ]
    
    def get_positions(self):
        """Get all positions."""
        from quantx.execution.brokers.base import Position
        positions = []
        for symbol, pos_dict in self._positions.items():
            if pos_dict.get("quantity", 0) != 0:
                positions.append(Position(
                    symbol=symbol,
                    quantity=pos_dict["quantity"],
                    average_price=pos_dict.get("average_price", 0.0),
                    current_price=pos_dict.get("average_price", 0.0),
                    market_value=pos_dict["quantity"] * pos_dict.get("average_price", 0.0),
                    unrealized_pnl=0.0,
                    realized_pnl=0.0
                ))
        return positions
    
    def get_position(self, symbol: str):
        """Get position for symbol."""
        from quantx.execution.brokers.base import Position
        if symbol in self._positions and self._positions[symbol].get("quantity", 0) != 0:
            pos_dict = self._positions[symbol]
            return Position(
                symbol=symbol,
                quantity=pos_dict["quantity"],
                average_price=pos_dict.get("average_price", 0.0),
                current_price=pos_dict.get("average_price", 0.0),
                market_value=pos_dict["quantity"] * pos_dict.get("average_price", 0.0),
                unrealized_pnl=0.0,
                realized_pnl=0.0
            )
        return None
    
    def get_account(self):
        """Get account information."""
        from quantx.execution.brokers.base import Account
        return Account(
            account_id="mock_account",
            cash=self._account.get("cash", 100000.0),
            equity=self._account.get("equity", 100000.0),
            buying_power=self._account.get("cash", 100000.0),
            positions_value=0.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            initial_capital=100000.0
        )
    
    def get_quote(self, symbol: str) -> Dict:
        """Get quote for symbol."""
        return {
            "symbol": symbol,
            "last_price": 1000.0,
            "bid": 999.5,
            "ask": 1000.5,
            "volume": 100000
        }
    
    # Helper methods for testing
    
    def set_position(self, symbol: str, quantity: int, average_price: float = 1000.0):
        """Set a position (for testing)."""
        self._positions[symbol] = {
            "quantity": quantity,
            "average_price": average_price
        }
    
    def set_account_balance(self, equity: float, cash: float):
        """Set account balance (for testing)."""
        self._account["equity"] = equity
        self._account["cash"] = cash
    
    def reset(self):
        """Reset broker state (for testing)."""
        self._orders.clear()
        self._positions.clear()
        self.placed_orders.clear()
        self.cancelled_orders.clear()
        self._next_order_id = 1
        self._account = {
            "equity": 100000.0,
            "cash": 100000.0,
            "margin_used": 0.0
        }
