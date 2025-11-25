"""
Portfolio Management for Backtesting

Tracks positions, cash, and calculates portfolio value and P&L.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger


@dataclass
class Position:
    """Represents a position in a symbol"""

    symbol: str
    quantity: int = 0
    avg_price: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    entry_time: Optional[datetime] = None

    def update(self, quantity: int, price: float, timestamp: datetime) -> None:
        """
        Update position with new trade

        Args:
            quantity: Quantity change (positive for buy, negative for sell)
            price: Trade price
            timestamp: Trade timestamp
        """
        if self.quantity == 0:
            # Opening new position
            self.avg_price = price
            self.quantity = quantity
            self.entry_time = timestamp
        elif (self.quantity > 0 and quantity > 0) or (self.quantity < 0 and quantity < 0):
            # Adding to position
            total_cost = (self.avg_price * abs(self.quantity)) + (price * abs(quantity))
            self.quantity += quantity
            self.avg_price = total_cost / abs(self.quantity)
        else:
            # Reducing or closing position
            if abs(quantity) >= abs(self.quantity):
                # Closing entire position
                self.realized_pnl += (price - self.avg_price) * abs(self.quantity) * (
                    1 if self.quantity > 0 else -1
                )
                self.quantity = 0
                self.avg_price = 0.0
                self.entry_time = None
            else:
                # Partial close
                self.realized_pnl += (price - self.avg_price) * abs(quantity) * (
                    1 if self.quantity > 0 else -1
                )
                self.quantity += quantity

    def calculate_unrealized_pnl(self, current_price: float) -> float:
        """
        Calculate unrealized P&L

        Args:
            current_price: Current market price

        Returns:
            Unrealized P&L
        """
        if self.quantity == 0:
            return 0.0

        self.unrealized_pnl = (current_price - self.avg_price) * abs(self.quantity) * (
            1 if self.quantity > 0 else -1
        )
        return self.unrealized_pnl


@dataclass
class Trade:
    """Represents a completed trade"""

    timestamp: datetime
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: int
    price: float
    commission: float
    total_cost: float
    pnl: float = 0.0


class Portfolio:
    """
    Portfolio management for backtesting

    Tracks cash, positions, and calculates portfolio metrics.
    """

    def __init__(
        self,
        initial_capital: float,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
    ) -> None:
        """
        Initialize portfolio

        Args:
            initial_capital: Starting capital
            commission_rate: Commission as fraction of trade value (default: 0.1%)
            slippage_rate: Slippage as fraction of price (default: 0.05%)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[tuple[datetime, float]] = []

        self._total_commission = 0.0
        self._total_slippage = 0.0

        logger.info(
            "Portfolio initialized: capital=${:,.2f}, commission={:.2%}, slippage={:.2%}",
            initial_capital,
            commission_rate,
            slippage_rate,
        )

    def execute_order(
        self, symbol: str, action: str, quantity: int, price: float, timestamp: datetime
    ) -> bool:
        """
        Execute an order

        Args:
            symbol: Symbol to trade
            action: 'buy' or 'sell'
            quantity: Quantity to trade
            price: Execution price
            timestamp: Execution timestamp

        Returns:
            True if order executed successfully
        """
        # Apply slippage
        if action == "buy":
            execution_price = price * (1 + self.slippage_rate)
        else:
            execution_price = price * (1 - self.slippage_rate)

        # Calculate costs
        trade_value = execution_price * quantity
        commission = trade_value * self.commission_rate
        total_cost = trade_value + commission

        # Check if we have enough cash for buy orders
        if action == "buy" and total_cost > self.cash:
            logger.warning(
                "Insufficient cash for order: need ${:,.2f}, have ${:,.2f}",
                total_cost,
                self.cash,
            )
            return False

        # Update cash
        if action == "buy":
            self.cash -= total_cost
            quantity_change = quantity
        else:
            self.cash += trade_value - commission
            quantity_change = -quantity

        # Update position
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)

        old_quantity = self.positions[symbol].quantity
        self.positions[symbol].update(quantity_change, execution_price, timestamp)

        # Calculate P&L for this trade
        pnl = 0.0
        if action == "sell":
            pnl = self.positions[symbol].realized_pnl

        # Record trade
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=execution_price,
            commission=commission,
            total_cost=total_cost,
            pnl=pnl,
        )
        self.trades.append(trade)

        # Update statistics
        self._total_commission += commission
        self._total_slippage += abs(execution_price - price) * quantity

        logger.debug(
            "Order executed: {} {} x{} @ ${:.2f} (commission: ${:.2f})",
            action.upper(),
            symbol,
            quantity,
            execution_price,
            commission,
        )

        return True

    def update_prices(self, prices: Dict[str, float], timestamp: datetime) -> None:
        """
        Update portfolio with current prices

        Args:
            prices: Dictionary of symbol -> price
            timestamp: Current timestamp
        """
        # Update unrealized P&L for all positions
        for symbol, position in self.positions.items():
            if symbol in prices and position.quantity != 0:
                position.calculate_unrealized_pnl(prices[symbol])

        # Record equity curve
        total_value = self.get_total_value(prices)
        self.equity_curve.append((timestamp, total_value))

    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value

        Args:
            current_prices: Dictionary of symbol -> price

        Returns:
            Total portfolio value
        """
        positions_value = sum(
            pos.quantity * current_prices.get(pos.symbol, 0.0)
            for pos in self.positions.values()
            if pos.quantity != 0
        )
        return self.cash + positions_value

    def get_total_pnl(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total P&L

        Args:
            current_prices: Dictionary of symbol -> price

        Returns:
            Total P&L
        """
        return self.get_total_value(current_prices) - self.initial_capital

    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for symbol

        Args:
            symbol: Symbol to get position for

        Returns:
            Position or None
        """
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        """
        Check if portfolio has position in symbol

        Args:
            symbol: Symbol to check

        Returns:
            True if has position
        """
        return symbol in self.positions and self.positions[symbol].quantity != 0

    def get_statistics(self, current_prices: Dict[str, float]) -> Dict:
        """
        Get portfolio statistics

        Args:
            current_prices: Current market prices

        Returns:
            Dictionary of statistics
        """
        total_value = self.get_total_value(current_prices)
        total_pnl = self.get_total_pnl(current_prices)

        realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        unrealized_pnl = sum(
            pos.calculate_unrealized_pnl(current_prices.get(pos.symbol, 0.0))
            for pos in self.positions.values()
            if pos.quantity != 0
        )

        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "total_value": total_value,
            "total_pnl": total_pnl,
            "total_return": total_pnl / self.initial_capital,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_commission": self._total_commission,
            "total_slippage": self._total_slippage,
            "num_trades": len(self.trades),
            "num_positions": sum(1 for pos in self.positions.values() if pos.quantity != 0),
        }
