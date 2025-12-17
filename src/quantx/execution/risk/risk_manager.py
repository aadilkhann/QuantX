"""
Risk Management System.

Provides comprehensive risk controls for live trading including position limits,
portfolio risk checks, and kill switch functionality.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger

from quantx.execution.brokers.base import Order, Position, Account, OrderSide


class RiskLevel(Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskLimits:
    """
    Risk limits configuration.
    
    Defines various risk limits for trading.
    """
    # Position-level limits
    max_position_size: float = 10000.0  # Maximum position size in currency
    max_position_pct: float = 0.10  # Maximum position as % of portfolio
    max_leverage: float = 1.0  # Maximum leverage allowed
    
    # Portfolio-level limits
    max_portfolio_risk: float = 0.20  # Maximum portfolio risk (20%)
    max_drawdown: float = 0.10  # Maximum drawdown threshold (10%)
    max_daily_loss: float = 1000.0  # Maximum daily loss in currency
    max_daily_loss_pct: float = 0.02  # Maximum daily loss as % (2%)
    
    # Exposure limits
    max_total_exposure: float = 100000.0  # Maximum total exposure
    max_sector_exposure: Optional[Dict[str, float]] = None  # Sector exposure limits
    max_long_exposure: float = 100000.0  # Maximum long exposure
    max_short_exposure: float = 50000.0  # Maximum short exposure
    
    # System-level limits
    max_orders_per_second: int = 10  # Maximum order rate
    max_orders_per_minute: int = 100  # Maximum orders per minute
    
    # Stop loss
    use_stop_loss: bool = True
    default_stop_loss_pct: float = 0.05  # 5% stop loss


class RiskViolation:
    """Represents a risk violation."""
    
    def __init__(
        self,
        level: RiskLevel,
        rule: str,
        message: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize risk violation.
        
        Args:
            level: Severity level
            rule: Rule that was violated
            message: Description of violation
            timestamp: When violation occurred
        """
        self.level = level
        self.rule = rule
        self.message = message
        self.timestamp = timestamp or datetime.now()
    
    def __str__(self) -> str:
        """String representation."""
        return f"[{self.level.value.upper()}] {self.rule}: {self.message}"


class RiskManager:
    """
    Comprehensive Risk Management System.
    
    Features:
    - Position-level risk checks
    - Portfolio-level risk monitoring
    - Drawdown tracking
    - Kill switch functionality
    - Order rate limiting
    - Exposure monitoring
    
    Example:
        >>> risk_mgr = RiskManager(limits)
        >>> is_safe, violations = risk_mgr.check_order(order, account, positions)
        >>> if not is_safe:
        ...     print(f"Order rejected: {violations}")
    """
    
    def __init__(
        self,
        limits: Optional[RiskLimits] = None,
        enable_kill_switch: bool = True
    ):
        """
        Initialize Risk Manager.
        
        Args:
            limits: Risk limits configuration
            enable_kill_switch: Enable kill switch
        """
        self.limits = limits or RiskLimits()
        self.enable_kill_switch = enable_kill_switch
        
        # State tracking
        self.kill_switch_active = False
        self.violations: List[RiskViolation] = []
        self.daily_pnl: float = 0.0
        self.peak_equity: float = 0.0
        self.current_drawdown: float = 0.0
        
        # Order rate tracking
        self.order_timestamps: List[datetime] = []
        
        # Callbacks
        self.on_violation: List[Callable[[RiskViolation], None]] = []
        self.on_kill_switch: List[Callable[[], None]] = []
        
        logger.info("Initialized Risk Manager")
    
    def check_order(
        self,
        order: Order,
        account: Account,
        positions: List[Position]
    ) -> tuple[bool, List[RiskViolation]]:
        """
        Pre-trade risk check for an order.
        
        Args:
            order: Order to check
            account: Current account state
            positions: Current positions
            
        Returns:
            Tuple of (is_safe, violations)
        """
        violations = []
        
        # Check kill switch
        if self.kill_switch_active:
            violations.append(RiskViolation(
                RiskLevel.CRITICAL,
                "kill_switch",
                "Kill switch is active - all trading halted"
            ))
            return False, violations
        
        # Check order rate limits
        rate_violations = self._check_order_rate()
        violations.extend(rate_violations)
        
        # Check position size
        position_violations = self._check_position_size(order, account)
        violations.extend(position_violations)
        
        # Check daily loss limit
        daily_loss_violations = self._check_daily_loss(order, account)
        violations.extend(daily_loss_violations)
        
        # Check exposure limits
        exposure_violations = self._check_exposure(order, account, positions)
        violations.extend(exposure_violations)
        
        # Check drawdown
        drawdown_violations = self._check_drawdown(account)
        violations.extend(drawdown_violations)
        
        # Trigger callbacks for violations
        for violation in violations:
            self._trigger_callbacks(self.on_violation, violation)
        
        # Determine if order is safe
        critical_violations = [v for v in violations if v.level == RiskLevel.CRITICAL]
        is_safe = len(critical_violations) == 0
        
        if not is_safe:
            logger.warning(f"Order failed risk check: {len(violations)} violation(s)")
            for v in violations:
                logger.warning(f"  {v}")
        
        return is_safe, violations
    
    def _check_order_rate(self) -> List[RiskViolation]:
        """Check order rate limits."""
        violations = []
        now = datetime.now()
        
        # Clean old timestamps
        one_second_ago = now - timedelta(seconds=1)
        one_minute_ago = now - timedelta(minutes=1)
        self.order_timestamps = [
            ts for ts in self.order_timestamps
            if ts > one_minute_ago
        ]
        
        # Check per-second limit
        recent_orders = sum(1 for ts in self.order_timestamps if ts > one_second_ago)
        if recent_orders >= self.limits.max_orders_per_second:
            violations.append(RiskViolation(
                RiskLevel.HIGH,
                "order_rate_per_second",
                f"Order rate limit exceeded: {recent_orders}/{self.limits.max_orders_per_second} per second"
            ))
        
        # Check per-minute limit
        if len(self.order_timestamps) >= self.limits.max_orders_per_minute:
            violations.append(RiskViolation(
                RiskLevel.MEDIUM,
                "order_rate_per_minute",
                f"Order rate limit exceeded: {len(self.order_timestamps)}/{self.limits.max_orders_per_minute} per minute"
            ))
        
        # Record this order timestamp
        self.order_timestamps.append(now)
        
        return violations
    
    def _check_position_size(
        self,
        order: Order,
        account: Account
    ) -> List[RiskViolation]:
        """Check position size limits."""
        violations = []
        
        # Estimate order value (approximate, actual may differ)
        estimated_value = order.quantity * (order.price or 0)
        if estimated_value == 0:
            # Can't check without price
            return violations
        
        # Check absolute position size
        if estimated_value > self.limits.max_position_size:
            violations.append(RiskViolation(
                RiskLevel.HIGH,
                "max_position_size",
                f"Position size ${estimated_value:,.2f} exceeds limit ${self.limits.max_position_size:,.2f}"
            ))
        
        # Check position size as percentage of portfolio
        if account.equity > 0:
            position_pct = estimated_value / account.equity
            if position_pct > self.limits.max_position_pct:
                violations.append(RiskViolation(
                    RiskLevel.HIGH,
                    "max_position_pct",
                    f"Position {position_pct:.1%} exceeds limit {self.limits.max_position_pct:.1%}"
                ))
        
        return violations
    
    def _check_daily_loss(
        self,
        order: Order,
        account: Account
    ) -> List[RiskViolation]:
        """Check daily loss limits."""
        violations = []
        
        # Check absolute daily loss
        if abs(self.daily_pnl) >= self.limits.max_daily_loss:
            violations.append(RiskViolation(
                RiskLevel.CRITICAL,
                "max_daily_loss",
                f"Daily loss ${abs(self.daily_pnl):,.2f} exceeds limit ${self.limits.max_daily_loss:,.2f}"
            ))
        
        # Check daily loss percentage
        if account.initial_capital > 0:
            daily_loss_pct = abs(self.daily_pnl) / account.initial_capital
            if daily_loss_pct >= self.limits.max_daily_loss_pct:
                violations.append(RiskViolation(
                    RiskLevel.CRITICAL,
                    "max_daily_loss_pct",
                    f"Daily loss {daily_loss_pct:.2%} exceeds limit {self.limits.max_daily_loss_pct:.2%}"
                ))
        
        return violations
    
    def _check_exposure(
        self,
        order: Order,
        account: Account,
        positions: List[Position]
    ) -> List[RiskViolation]:
        """Check exposure limits."""
        violations = []
        
        # Calculate current exposure
        total_long = sum(pos.market_value for pos in positions if pos.quantity > 0)
        total_short = sum(abs(pos.market_value) for pos in positions if pos.quantity < 0)
        
        # Estimate new exposure after order
        estimated_value = order.quantity * (order.price or 0)
        if order.side == OrderSide.BUY:
            new_long = total_long + estimated_value
            if new_long > self.limits.max_long_exposure:
                violations.append(RiskViolation(
                    RiskLevel.HIGH,
                    "max_long_exposure",
                    f"Long exposure ${new_long:,.2f} exceeds limit ${self.limits.max_long_exposure:,.2f}"
                ))
        else:
            new_short = total_short + estimated_value
            if new_short > self.limits.max_short_exposure:
                violations.append(RiskViolation(
                    RiskLevel.HIGH,
                    "max_short_exposure",
                    f"Short exposure ${new_short:,.2f} exceeds limit ${self.limits.max_short_exposure:,.2f}"
                ))
        
        # Check total exposure
        new_total_exposure = total_long + total_short + estimated_value
        if new_total_exposure > self.limits.max_total_exposure:
            violations.append(RiskViolation(
                RiskLevel.HIGH,
                "max_total_exposure",
                f"Total exposure ${new_total_exposure:,.2f} exceeds limit ${self.limits.max_total_exposure:,.2f}"
            ))
        
        return violations
    
    def _check_drawdown(self, account: Account) -> List[RiskViolation]:
        """Check drawdown limits."""
        violations = []
        
        # Update peak equity
        if account.equity > self.peak_equity:
            self.peak_equity = account.equity
        
        # Calculate drawdown
        if self.peak_equity > 0:
            self.current_drawdown = (self.peak_equity - account.equity) / self.peak_equity
            
            if self.current_drawdown >= self.limits.max_drawdown:
                violations.append(RiskViolation(
                    RiskLevel.CRITICAL,
                    "max_drawdown",
                    f"Drawdown {self.current_drawdown:.2%} exceeds limit {self.limits.max_drawdown:.2%}"
                ))
        
        return violations
    
    def update_daily_pnl(self, pnl: float):
        """
        Update daily P&L.
        
        Args:
            pnl: Current daily P&L
        """
        self.daily_pnl = pnl
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of each trading day)."""
        self.daily_pnl = 0.0
        self.order_timestamps.clear()
        logger.info("Reset daily risk metrics")
    
    def trigger_kill_switch(self, reason: str = "Manual trigger"):
        """
        Activate kill switch to halt all trading.
        
        Args:
            reason: Reason for triggering kill switch
        """
        if not self.enable_kill_switch:
            logger.warning("Kill switch is disabled")
            return
        
        self.kill_switch_active = True
        
        violation = RiskViolation(
            RiskLevel.CRITICAL,
            "kill_switch",
            f"Kill switch activated: {reason}"
        )
        self.violations.append(violation)
        
        # Trigger callbacks
        self._trigger_callbacks(self.on_kill_switch)
        
        logger.critical(f"KILL SWITCH ACTIVATED: {reason}")
    
    def deactivate_kill_switch(self):
        """Deactivate kill switch to resume trading."""
        self.kill_switch_active = False
        logger.info("Kill switch deactivated - trading resumed")
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get current risk metrics.
        
        Returns:
            Dictionary of risk metrics
        """
        return {
            "kill_switch_active": self.kill_switch_active,
            "daily_pnl": self.daily_pnl,
            "current_drawdown": self.current_drawdown,
            "peak_equity": self.peak_equity,
            "recent_orders_per_second": len([
                ts for ts in self.order_timestamps
                if ts > datetime.now() - timedelta(seconds=1)
            ]),
            "recent_orders_per_minute": len(self.order_timestamps),
            "total_violations": len(self.violations),
            "active_violations": len([
                v for v in self.violations
                if v.timestamp > datetime.now() - timedelta(hours=1)
            ])
        }
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register a callback for an event.
        
        Args:
            event: Event name (violation, kill_switch)
            callback: Callback function
        """
        if event == "violation":
            self.on_violation.append(callback)
        elif event == "kill_switch":
            self.on_kill_switch.append(callback)
        else:
            logger.warning(f"Unknown event: {event}")
    
    def _trigger_callbacks(self, callbacks: List[Callable], *args):
        """Trigger callbacks with error handling."""
        for callback in callbacks:
            try:
                callback(*args)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
