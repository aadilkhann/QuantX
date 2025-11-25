"""
Moving Average Crossover Strategy

Example rule-based strategy using moving average crossover signals.
"""

from typing import Any, Dict

import pandas as pd
from loguru import logger

from quantx.core.events import Event, EventType
from quantx.strategies.base import RuleBasedStrategy
from quantx.strategies.registry import StrategyRegistry


@StrategyRegistry.register("ma_crossover")
class MACrossoverStrategy(RuleBasedStrategy):
    """
    Moving Average Crossover Strategy

    Generates buy signals when fast MA crosses above slow MA,
    and sell signals when fast MA crosses below slow MA.
    """

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        """
        Initialize MA Crossover strategy

        Args:
            name: Strategy name
            config: Configuration with keys:
                - fast_period: Fast MA period (default: 50)
                - slow_period: Slow MA period (default: 200)
                - symbols: List of symbols to trade
        """
        super().__init__(name, config)

        self.fast_period = config.get("fast_period", 50)
        self.slow_period = config.get("slow_period", 200)
        self.symbols = config.get("symbols", [])

        # Store price history for each symbol
        self._price_history: Dict[str, pd.Series] = {symbol: pd.Series(dtype=float) for symbol in self.symbols}

        # Track previous MA values to detect crossovers
        self._prev_fast_ma: Dict[str, float] = {}
        self._prev_slow_ma: Dict[str, float] = {}

        logger.info(
            "MACrossoverStrategy initialized: fast={}, slow={}, symbols={}",
            self.fast_period,
            self.slow_period,
            self.symbols,
        )

    def on_data(self, event: Event) -> None:
        """
        Process market data and generate signals

        Args:
            event: Market data event
        """
        if event.event_type != EventType.MARKET_DATA:
            return

        data = event.data
        symbol = data.get("symbol")
        close_price = data.get("close")

        if symbol not in self.symbols:
            return

        # Update price history
        self._price_history[symbol] = pd.concat([
            self._price_history[symbol],
            pd.Series([close_price])
        ])

        # Keep only necessary history
        max_period = max(self.fast_period, self.slow_period)
        if len(self._price_history[symbol]) > max_period * 2:
            self._price_history[symbol] = self._price_history[symbol].iloc[-max_period * 2:]

        # Need enough data for both MAs
        if len(self._price_history[symbol]) < self.slow_period:
            logger.trace("Not enough data for {}: {} bars", symbol, len(self._price_history[symbol]))
            return

        # Calculate moving averages
        fast_ma = self._price_history[symbol].rolling(window=self.fast_period).mean().iloc[-1]
        slow_ma = self._price_history[symbol].rolling(window=self.slow_period).mean().iloc[-1]

        # Get previous MA values
        prev_fast = self._prev_fast_ma.get(symbol)
        prev_slow = self._prev_slow_ma.get(symbol)

        # Detect crossovers
        if prev_fast is not None and prev_slow is not None:
            # Bullish crossover: fast MA crosses above slow MA
            if prev_fast <= prev_slow and fast_ma > slow_ma:
                if not self.has_position(symbol):
                    logger.info(
                        "Bullish crossover detected for {}: fast={:.2f}, slow={:.2f}",
                        symbol,
                        fast_ma,
                        slow_ma,
                    )
                    # Calculate position size (simple: 100 shares)
                    quantity = 100
                    self.buy(symbol, quantity)

            # Bearish crossover: fast MA crosses below slow MA
            elif prev_fast >= prev_slow and fast_ma < slow_ma:
                if self.has_position(symbol):
                    logger.info(
                        "Bearish crossover detected for {}: fast={:.2f}, slow={:.2f}",
                        symbol,
                        fast_ma,
                        slow_ma,
                    )
                    # Sell entire position
                    position = self.get_position(symbol)
                    self.sell(symbol, position)

        # Store current MA values for next iteration
        self._prev_fast_ma[symbol] = fast_ma
        self._prev_slow_ma[symbol] = slow_ma

    def on_fill(self, event: Event) -> None:
        """
        Process order fill

        Args:
            event: Fill event
        """
        if event.event_type != EventType.FILL:
            return

        data = event.data
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        action = data.get("action")

        # Update position
        if action == "buy":
            self.update_position(symbol, quantity)
        elif action == "sell":
            self.update_position(symbol, -quantity)

        logger.info(
            "Fill processed for {}: {} x{}, new position: {}",
            symbol,
            action,
            quantity,
            self.get_position(symbol),
        )
