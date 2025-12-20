"""
Live P&L Tracking for Live Trading.

Real-time profit and loss calculation and reporting for live trading sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

from loguru import logger

from quantx.execution.brokers.base import Position, Fill


@dataclass
class TradeRecord:
    """Record of a completed trade."""
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    side: str  # "long" or "short"
    pnl: float
    pnl_pct: float
    commission: float
    net_pnl: float


@dataclass
class DailyPnL:
    """Daily P&L summary."""
    date: date
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    commission: float = 0.0
    trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    
    @property
    def total_pnl(self) -> float:
        """Get total P&L."""
        return self.realized_pnl + self.unrealized_pnl
    
    @property
    def net_pnl(self) -> float:
        """Get net P&L after commission."""
        return self.total_pnl - self.commission
    
    @property
    def win_rate(self) -> float:
        """Get win rate."""
        if self.trades == 0:
            return 0.0
        return self.winning_trades / self.trades * 100


@dataclass
class LivePnLSnapshot:
    """Real-time P&L snapshot."""
    timestamp: datetime
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    daily_pnl: float
    total_commission: float
    open_positions: int
    closed_trades: int
    win_rate: float
    max_drawdown: float
    current_drawdown: float


class LivePnLTracker:
    """
    Live P&L tracker.
    
    Tracks real-time profit and loss with mark-to-market calculation,
    daily summaries, and performance metrics.
    
    Example:
        >>> tracker = LivePnLTracker(initial_capital=100000)
        >>> tracker.update_position_pnl("AAPL", 100, 150.0, 155.0)
        >>> tracker.record_trade(...)
        >>> snapshot = tracker.get_snapshot()
        >>> print(f"Total P&L: ${snapshot.total_pnl:,.2f}")
    """
    
    def __init__(self, initial_capital: float = 0.0):
        """
        Initialize P&L tracker.
        
        Args:
            initial_capital: Starting capital
        """
        self.initial_capital = initial_capital
        self.start_time = datetime.now()
        
        # P&L tracking
        self.realized_pnl = 0.0
        self.total_commission = 0.0
        
        # Position tracking for unrealized P&L
        self._position_pnl: Dict[str, float] = {}  # symbol -> unrealized P&L
        
        # Daily P&L
        self._daily_pnl: Dict[date, DailyPnL] = defaultdict(lambda: DailyPnL(date=date.today()))
        
        # Trade history
        self._trades: List[TradeRecord] = []
        
        # Performance tracking
        self._equity_curve: List[tuple[datetime, float]] = [(self.start_time, initial_capital)]
        self._peak_equity = initial_capital
        self._max_drawdown = 0.0
        
        logger.info(f"LivePnLTracker initialized with ${initial_capital:,.2f}")
    
    def update_position_pnl(
        self,
        symbol: str,
        quantity: float,
        average_price: float,
        current_price: float
    ) -> float:
        """
        Update unrealized P&L for a position.
        
        Args:
            symbol: Trading symbol
            quantity: Position quantity
            average_price: Average entry price
            current_price: Current market price
            
        Returns:
            Unrealized P&L for this position
        """
        if quantity == 0:
            self._position_pnl[symbol] = 0.0
            return 0.0
        
        # Calculate unrealized P&L
        pnl = (current_price - average_price) * quantity
        self._position_pnl[symbol] = pnl
        
        logger.debug(f"Updated {symbol} P&L: ${pnl:,.2f} ({quantity} @ {average_price} -> {current_price})")
        
        return pnl
    
    def update_from_positions(self, positions: List[Position]) -> None:
        """
        Update unrealized P&L from list of positions.
        
        Args:
            positions: List of Position objects
        """
        for position in positions:
            self.update_position_pnl(
                symbol=position.symbol,
                quantity=position.quantity,
                average_price=position.average_price,
                current_price=position.current_price
            )
    
    def record_trade(
        self,
        symbol: str,
        entry_time: datetime,
        exit_time: datetime,
        entry_price: float,
        exit_price: float,
        quantity: float,
        side: str = "long",
        commission: float = 0.0
    ) -> TradeRecord:
        """
        Record a completed trade.
        
        Args:
            symbol: Trading symbol
            entry_time: Entry timestamp
            exit_time: Exit timestamp
            entry_price: Entry price
            exit_price: Exit price
            quantity: Trade quantity
            side: "long" or "short"
            commission: Total commission for the trade
            
        Returns:
            TradeRecord
        """
        # Calculate P&L
        if side == "long":
            pnl = (exit_price - entry_price) * quantity
        else:  # short
            pnl = (entry_price - exit_price) * quantity
        
        pnl_pct = (pnl / (entry_price * quantity)) * 100 if (entry_price * quantity) != 0 else 0.0
        net_pnl = pnl - commission
        
        # Create trade record
        trade = TradeRecord(
            symbol=symbol,
            entry_time=entry_time,
            exit_time=exit_time,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            side=side,
            pnl=pnl,
            pnl_pct=pnl_pct,
            commission=commission,
            net_pnl=net_pnl
        )
        
        # Update totals
        self.realized_pnl += net_pnl
        self.total_commission += commission
        
        # Update daily P&L
        today = exit_time.date()
        daily = self._daily_pnl[today]
        daily.realized_pnl += net_pnl
        daily.commission += commission
        daily.trades += 1
        
        if net_pnl > 0:
            daily.winning_trades += 1
        elif net_pnl < 0:
            daily.losing_trades += 1
        
        # Save trade
        self._trades.append(trade)
        
        # Update equity curve
        current_equity = self.get_total_equity()
        self._equity_curve.append((exit_time, current_equity))
        
        # Update peak and drawdown
        if current_equity > self._peak_equity:
            self._peak_equity = current_equity
        
        drawdown = (self._peak_equity - current_equity) / self._peak_equity * 100 if self._peak_equity > 0 else 0.0
        if drawdown > self._max_drawdown:
            self._max_drawdown = drawdown
        
        logger.info(
            f"📊 Trade recorded: {symbol} {side} {quantity} @ {entry_price} -> {exit_price} "
            f"= ${net_pnl:,.2f} ({pnl_pct:+.2f}%)"
        )
        
        return trade
    
    def record_fill(self, fill: Fill, is_entry: bool = False, entry_price: Optional[float] = None) -> Optional[TradeRecord]:
        """
        Record a fill (handles trade completion automatically).
        
        Args:
            fill: Fill object
            is_entry: Whether this is an entry (True) or exit (False)
            entry_price: Entry price if this is an exit
            
        Returns:
            TradeRecord if trade completed, None otherwise
        """
        # Update commission
        self.total_commission += fill.commission
        
        if not is_entry and entry_price is not None:
            # This is an exit - record completed trade
            side = "long" if fill.side.value == "sell" else "short"
            
            return self.record_trade(
                symbol=fill.symbol,
                entry_time=fill.timestamp - timedelta(hours=1),  # Approximate, should track actual entry time
                exit_time=fill.timestamp,
                entry_price=entry_price,
                exit_price=fill.price,
                quantity=fill.quantity,
                side=side,
                commission=fill.commission
            )
        
        return None
    
    def get_unrealized_pnl(self) -> float:
        """Get total unrealized P&L."""
        return sum(self._position_pnl.values())
    
    def get_total_pnl(self) -> float:
        """Get total P&L (realized + unrealized)."""
        return self.realized_pnl + self.get_unrealized_pnl()
    
    def get_total_equity(self) -> float:
        """Get total equity."""
        return self.initial_capital + self.get_total_pnl()
    
    def get_current_drawdown(self) -> float:
        """Get current drawdown percentage."""
        current_equity = self.get_total_equity()
        if self._peak_equity == 0:
            return 0.0
        return (self._peak_equity - current_equity) / self._peak_equity * 100
    
    def get_daily_pnl(self, target_date: Optional[date] = None) -> DailyPnL:
        """
        Get P&L for a specific date.
        
        Args:
            target_date: Date to get P&L for (default: today)
            
        Returns:
            DailyPnL object
        """
        if target_date is None:
            target_date = date.today()
        
        daily = self._daily_pnl[target_date]
        
        # Update unrealized P&L for today
        if target_date == date.today():
            daily.unrealized_pnl = self.get_unrealized_pnl()
        
        return daily
    
    def get_snapshot(self) -> LivePnLSnapshot:
        """
        Get current P&L snapshot.
        
        Returns:
            LivePnLSnapshot
        """
        unrealized = self.get_unrealized_pnl()
        total = self.realized_pnl + unrealized
        daily_pnl = self.get_daily_pnl()
        
        # Calculate win rate
        winning_trades = len([t for t in self._trades if t.net_pnl > 0])
        total_trades = len(self._trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        return LivePnLSnapshot(
            timestamp=datetime.now(),
            unrealized_pnl=unrealized,
            realized_pnl=self.realized_pnl,
            total_pnl=total,
            daily_pnl=daily_pnl.net_pnl,
            total_commission=self.total_commission,
            open_positions=len([pnl for pnl in self._position_pnl.values() if pnl != 0]),
            closed_trades=total_trades,
            win_rate=win_rate,
            max_drawdown=self._max_drawdown,
            current_drawdown=self.get_current_drawdown()
        )
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary."""
        snapshot = self.get_snapshot()
        total_trades = len(self._trades)
        
        if total_trades == 0:
            return {
                'total_pnl': snapshot.total_pnl,
                'realized_pnl': snapshot.realized_pnl,
                'unrealized_pnl': snapshot.unrealized_pnl,
                'total_trades': 0
            }
        
        winning_trades = [t for t in self._trades if t.net_pnl > 0]
        losing_trades = [t for t in self._trades if t.net_pnl < 0]
        
        avg_win = sum(t.net_pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(t.net_pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
        
        profit_factor = (
            abs(sum(t.net_pnl for t in winning_trades)) / abs(sum(t.net_pnl for t in losing_trades))
            if losing_trades and sum(t.net_pnl for t in losing_trades) != 0
            else 0.0
        )
        
        return {
            'total_pnl': snapshot.total_pnl,
            'realized_pnl': snapshot.realized_pnl,
            'unrealized_pnl': snapshot.unrealized_pnl,
            'daily_pnl': snapshot.daily_pnl,
            'total_commission': snapshot.total_commission,
            'net_pnl': snapshot.total_pnl - snapshot.total_commission,
            'return_pct': (snapshot.total_pnl / self.initial_capital * 100) if self.initial_capital > 0 else 0.0,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': snapshot.win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': snapshot.max_drawdown,
            'current_drawdown': snapshot.current_drawdown,
            'equity': self.get_total_equity(),
            'open_positions': snapshot.open_positions
        }
    
    def get_trades(self, limit: Optional[int] = None) -> List[TradeRecord]:
        """
        Get trade history.
        
        Args:
            limit: Maximum number of trades to return (most recent first)
            
        Returns:
            List of TradeRecord objects
        """
        trades = sorted(self._trades, key=lambda t: t.exit_time, reverse=True)
        if limit:
            return trades[:limit]
        return trades
    
    def get_equity_curve(self) -> List[tuple[datetime, float]]:
        """Get equity curve data."""
        return self._equity_curve.copy()
    
    def reset_daily(self) -> None:
        """Reset daily counters (call at start of new trading day)."""
        today = date.today()
        if today not in self._daily_pnl:
            self._daily_pnl[today] = DailyPnL(date=today)
            logger.info(f"Started new trading day: {today}")
