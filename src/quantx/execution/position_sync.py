"""
Position Synchronization for Live Trading.

Ensures strategy positions stay in sync with broker positions and handles
reconciliation of discrepancies.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger

from quantx.execution.brokers.base import IBroker, Position


class DiscrepancyType(Enum):
    """Types of position discrepancies."""
    MISSING_LOCAL = "missing_local"  # Position exists at broker but not locally
    MISSING_BROKER = "missing_broker"  # Position exists locally but not at broker
    QUANTITY_MISMATCH = "quantity_mismatch"  # Quantities don't match
    PRICE_MISMATCH = "price_mismatch"  # Average prices don't match


@dataclass
class PositionDiscrepancy:
    """Position discrepancy report."""
    symbol: str
    type: DiscrepancyType
    local_quantity: float
    broker_quantity: float
    local_price: Optional[float] = None
    broker_price: Optional[float] = None
    timestamp: datetime = datetime.now()
    resolved: bool = False


@dataclass
class ReconciliationReport:
    """Position reconciliation report."""
    timestamp: datetime
    total_positions_local: int
    total_positions_broker: int
    discrepancies: List[PositionDiscrepancy]
    synced: bool
    
    @property
    def has_discrepancies(self) -> bool:
        """Check if there are unresolved discrepancies."""
        return len([d for d in self.discrepancies if not d.resolved]) > 0
    
    def get_summary(self) -> Dict:
        """Get summary of reconciliation."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'synced': self.synced,
            'total_discrepancies': len(self.discrepancies),
            'unresolved_discrepancies': len([d for d in self.discrepancies if not d.resolved]),
            'local_positions': self.total_positions_local,
            'broker_positions': self.total_positions_broker
        }


class PositionSynchronizer:
    """
    Position synchronizer for live trading.
    
    Keeps strategy positions in sync with broker positions and detects
    any discrepancies that need reconciliation.
    
    Example:
        >>> sync = PositionSynchronizer(broker, auto_reconcile=True)
        >>> report = sync.sync_positions(strategy._positions)
        >>> if report.has_discrepancies:
        ...     print(f"Found {len(report.discrepancies)} discrepancies")
    """
    
    def __init__(
        self,
        broker: IBroker,
        auto_reconcile: bool = True,
        tolerance: float = 0.01  # 1% tolerance for price mismatches
    ):
        """
        Initialize position synchronizer.
        
        Args:
            broker: Broker instance
            auto_reconcile: Automatically fix discrepancies
            tolerance: Price mismatch tolerance (percentage)
        """
        self.broker = broker
        self.auto_reconcile = auto_reconcile
        self.tolerance = tolerance
        
        # History
        self.reconciliation_history: List[ReconciliationReport] = []
        self.sync_count = 0
        self.discrepancy_count = 0
        
        logger.info(f"PositionSynchronizer initialized (auto_reconcile={auto_reconcile})")
    
    def sync_positions(
        self,
        local_positions: Dict[str, float],
        local_prices: Optional[Dict[str, float]] = None
    ) -> ReconciliationReport:
        """
        Synchronize local positions with broker positions.
        
        Args:
            local_positions: Dictionary of symbol -> quantity
            local_prices: Optional dictionary of symbol -> average_price
            
        Returns:
            ReconciliationReport
        """
        self.sync_count += 1
        logger.debug(f"Starting position sync #{self.sync_count}")
        
        # Get broker positions
        broker_positions = self._get_broker_positions()
        broker_dict = {p.symbol: p for p in broker_positions}
        
        # Find discrepancies
        discrepancies = []
        
        # Check all local positions
        for symbol, quantity in local_positions.items():
            if quantity == 0:
                continue  # Skip closed positions
            
            if symbol not in broker_dict:
                # Local position missing from broker
                discrepancies.append(PositionDiscrepancy(
                    symbol=symbol,
                    type=DiscrepancyType.MISSING_BROKER,
                    local_quantity=quantity,
                    broker_quantity=0.0
                ))
            else:
                broker_pos = broker_dict[symbol]
                
                # Check quantity mismatch
                if abs(broker_pos.quantity - quantity) > 0.001:  # Small tolerance for floating point
                    discrepancies.append(PositionDiscrepancy(
                        symbol=symbol,
                        type=DiscrepancyType.QUANTITY_MISMATCH,
                        local_quantity=quantity,
                        broker_quantity=broker_pos.quantity,
                        local_price=local_prices.get(symbol) if local_prices else None,
                        broker_price=broker_pos.average_price
                    ))
                
                # Check price mismatch (if local prices provided)
                if local_prices and symbol in local_prices:
                    local_price = local_prices[symbol]
                    broker_price = broker_pos.average_price
                    
                    if abs(broker_price - local_price) / broker_price > self.tolerance:
                        discrepancies.append(PositionDiscrepancy(
                            symbol=symbol,
                            type=DiscrepancyType.PRICE_MISMATCH,
                            local_quantity=quantity,
                            broker_quantity=broker_pos.quantity,
                            local_price=local_price,
                            broker_price=broker_price
                        ))
        
        # Check broker positions missing from local
        for symbol, broker_pos in broker_dict.items():
            if broker_pos.quantity == 0:
                continue
            
            if symbol not in local_positions or local_positions[symbol] == 0:
                discrepancies.append(PositionDiscrepancy(
                    symbol=symbol,
                    type=DiscrepancyType.MISSING_LOCAL,
                    local_quantity=0.0,
                    broker_quantity=broker_pos.quantity,
                    broker_price=broker_pos.average_price
                ))
        
        # Create report
        report = ReconciliationReport(
            timestamp=datetime.now(),
            total_positions_local=len([q for q in local_positions.values() if q != 0]),
            total_positions_broker=len([p for p in broker_positions if p.quantity != 0]),
            discrepancies=discrepancies,
            synced=len(discrepancies) == 0
        )
        
        # Log results
        if report.synced:
            logger.info(f"✅ Positions synced successfully ({report.total_positions_broker} positions)")
        else:
            logger.warning(f"⚠️ Found {len(discrepancies)} position discrepancies")
            for disc in discrepancies:
                logger.warning(f"  - {disc.symbol}: {disc.type.value} (local={disc.local_quantity}, broker={disc.broker_quantity})")
            
            self.discrepancy_count += len(discrepancies)
        
        # Auto-reconcile if enabled
        if self.auto_reconcile and not report.synced:
            self._reconcile_discrepancies(local_positions, discrepancies)
        
        # Save to history
        self.reconciliation_history.append(report)
        
        return report
    
    def _get_broker_positions(self) -> List[Position]:
        """Get positions from broker."""
        try:
            return self.broker.get_positions()
        except Exception as e:
            logger.error(f"Failed to get broker positions: {e}")
            return []
    
    def _reconcile_discrepancies(
        self,
        local_positions: Dict[str, float],
        discrepancies: List[PositionDiscrepancy]
    ) -> None:
        """
        Automatically reconcile position discrepancies.
        
        Args:
            local_positions: Local positions dictionary (will be modified)
            discrepancies: List of discrepancies to fix
        """
        logger.info("Auto-reconciling position discrepancies...")
        
        for disc in discrepancies:
            if disc.type == DiscrepancyType.MISSING_LOCAL:
                # Add missing position from broker
                local_positions[disc.symbol] = disc.broker_quantity
                disc.resolved = True
                logger.info(f"  Added missing position: {disc.symbol} = {disc.broker_quantity}")
            
            elif disc.type == DiscrepancyType.MISSING_BROKER:
                # Remove position that doesn't exist at broker
                local_positions[disc.symbol] = 0
                disc.resolved = True
                logger.info(f"  Removed orphaned position: {disc.symbol}")
            
            elif disc.type == DiscrepancyType.QUANTITY_MISMATCH:
                # Trust broker quantity
                local_positions[disc.symbol] = disc.broker_quantity
                disc.resolved = True
                logger.info(f"  Fixed quantity: {disc.symbol} {disc.local_quantity} -> {disc.broker_quantity}")
            
            elif disc.type == DiscrepancyType.PRICE_MISMATCH:
                # Price mismatch - log but don't auto-fix (might need manual review)
                logger.warning(f"  Price mismatch for {disc.symbol}: local={disc.local_price}, broker={disc.broker_price}")
                # Don't mark as resolved - needs manual review
        
        resolved_count = len([d for d in discrepancies if d.resolved])
        logger.info(f"Reconciled {resolved_count}/{len(discrepancies)} discrepancies")
    
    def force_sync_from_broker(self, local_positions: Dict[str, float]) -> None:
        """
        Force local positions to match broker exactly.
        
        Args:
            local_positions: Local positions dictionary (will be replaced)
        """
        logger.warning("Force syncing from broker - this will overwrite all local positions!")
        
        broker_positions = self._get_broker_positions()
        
        # Clear local positions
        local_positions.clear()
        
        # Copy from broker
        for pos in broker_positions:
            if pos.quantity != 0:
                local_positions[pos.symbol] = pos.quantity
        
        logger.info(f"Force sync complete: {len(local_positions)} positions")
    
    def get_statistics(self) -> Dict:
        """Get synchronization statistics."""
        return {
            'sync_count': self.sync_count,
            'total_discrepancies': self.discrepancy_count,
            'last_sync': self.reconciliation_history[-1].timestamp.isoformat() if self.reconciliation_history else None,
            'last_sync_status': self.reconciliation_history[-1].synced if self.reconciliation_history else None
        }
    
    def get_recent_reports(self, count: int = 10) -> List[ReconciliationReport]:
        """
        Get recent reconciliation reports.
        
        Args:
            count: Number of reports to return
            
        Returns:
            List of recent reports
        """
        return self.reconciliation_history[-count:]
