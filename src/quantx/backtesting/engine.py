"""
Backtesting Engine for QuantX

Event-driven backtesting engine that simulates trading strategies on historical data.
"""

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from quantx.core.events import Event, EventBus, EventType
from quantx.data.base import IDataProvider
from quantx.strategies.base import BaseStrategy
from quantx.backtesting.portfolio import Portfolio
from quantx.backtesting.metrics import PerformanceMetrics


class BacktestEngine:
    """
    Event-driven backtesting engine

    Simulates trading strategies on historical data with realistic
    order execution and transaction costs.
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        data_provider: IDataProvider,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
    ) -> None:
        """
        Initialize backtest engine

        Args:
            strategy: Trading strategy to backtest
            data_provider: Data provider for historical data
            initial_capital: Starting capital
            commission_rate: Commission as fraction of trade value
            slippage_rate: Slippage as fraction of price
        """
        self.strategy = strategy
        self.data_provider = data_provider
        self.initial_capital = initial_capital

        # Create portfolio
        self.portfolio = Portfolio(
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            slippage_rate=slippage_rate,
        )

        # Create event bus
        self.event_bus = EventBus()

        # Set up strategy
        self.strategy.set_event_bus(self.event_bus)
        self.strategy.set_portfolio(self.portfolio)

        # Subscribe to events
        self.event_bus.subscribe(EventType.SIGNAL, self._on_signal)

        # Backtest state
        self._current_prices: Dict[str, float] = {}
        self._is_running = False

        logger.info("BacktestEngine initialized with strategy: {}", strategy.name)

    def run(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> Dict:
        """
        Run backtest

        Args:
            symbols: List of symbols to trade
            start_date: Backtest start date
            end_date: Backtest end date
            interval: Data interval (1d, 1h, etc.)

        Returns:
            Dictionary with backtest results
        """
        logger.info("=" * 60)
        logger.info("STARTING BACKTEST")
        logger.info("=" * 60)
        logger.info("Strategy: {}", self.strategy.name)
        logger.info("Symbols: {}", symbols)
        logger.info("Period: {} to {}", start_date.date(), end_date.date())
        logger.info("Initial Capital: ${:,.2f}", self.initial_capital)
        logger.info("=" * 60 + "\n")

        # Start event bus
        self.event_bus.start()
        self._is_running = True

        # Call strategy start
        self.strategy.on_start()

        try:
            # Fetch historical data for all symbols
            data_dict = {}
            for symbol in symbols:
                logger.info("Fetching data for {}...", symbol)
                data = self.data_provider.get_historical_data(
                    symbol, start_date, end_date, interval
                )
                data_dict[symbol] = data
                logger.info("Fetched {} bars for {}", len(data), symbol)

            # Align all data to same timestamps
            aligned_data = self._align_data(data_dict)

            logger.info("\nRunning backtest on {} time steps...\n", len(aligned_data))

            # Main backtest loop
            for idx, (timestamp, prices) in enumerate(aligned_data.items()):
                # Update current prices
                self._current_prices = prices

                # Publish market data events for each symbol
                for symbol, price_data in prices.items():
                    event = Event(
                        priority=0,
                        event_type=EventType.MARKET_DATA,
                        timestamp=timestamp,
                        data={
                            "symbol": symbol,
                            "open": price_data["open"],
                            "high": price_data["high"],
                            "low": price_data["low"],
                            "close": price_data["close"],
                            "volume": price_data["volume"],
                        },
                        source="backtest",
                    )
                    self.event_bus.publish(event)

                # Give event bus time to process
                import time

                time.sleep(0.001)

                # Update portfolio with current prices
                current_close_prices = {
                    symbol: data["close"] for symbol, data in prices.items()
                }
                self.portfolio.update_prices(current_close_prices, timestamp)

                # Log progress
                if (idx + 1) % 50 == 0 or idx == len(aligned_data) - 1:
                    progress = (idx + 1) / len(aligned_data) * 100
                    total_value = self.portfolio.get_total_value(current_close_prices)
                    logger.info(
                        "Progress: {:.1f}% | Portfolio Value: ${:,.2f}",
                        progress,
                        total_value,
                    )

        finally:
            # Stop event bus
            self.event_bus.stop()
            self._is_running = False

            # Call strategy stop
            self.strategy.on_stop()

        # Calculate final results
        results = self._calculate_results()

        logger.info("\n" + "=" * 60)
        logger.info("BACKTEST COMPLETE")
        logger.info("=" * 60 + "\n")

        return results

    def _align_data(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[datetime, Dict]:
        """
        Align data from multiple symbols to same timestamps

        Args:
            data_dict: Dictionary of symbol -> DataFrame

        Returns:
            Dictionary of timestamp -> {symbol -> price_data}
        """
        # Get all unique timestamps
        all_timestamps = set()
        for df in data_dict.values():
            all_timestamps.update(df.index)

        aligned = {}
        for timestamp in sorted(all_timestamps):
            aligned[timestamp] = {}
            for symbol, df in data_dict.items():
                if timestamp in df.index:
                    row = df.loc[timestamp]
                    aligned[timestamp][symbol] = {
                        "open": row["open"],
                        "high": row["high"],
                        "low": row["low"],
                        "close": row["close"],
                        "volume": row["volume"],
                    }

        return aligned

    def _on_signal(self, event: Event) -> None:
        """
        Handle signal events from strategy

        Args:
            event: Signal event
        """
        if not self._is_running:
            return

        data = event.data
        symbol = data.get("symbol")
        action = data.get("action")
        quantity = data.get("quantity")
        price = data.get("price")

        # Use current market price if not specified
        if price is None:
            if symbol in self._current_prices:
                price = self._current_prices[symbol]["close"]
            else:
                logger.warning("No price available for {}, skipping signal", symbol)
                return

        # Execute order
        success = self.portfolio.execute_order(
            symbol=symbol,
            action=action.value if hasattr(action, "value") else action,
            quantity=quantity,
            price=price,
            timestamp=event.timestamp,
        )

        if success:
            # Publish fill event
            fill_event = Event(
                priority=2,
                event_type=EventType.FILL,
                timestamp=event.timestamp,
                data={
                    "symbol": symbol,
                    "action": action.value if hasattr(action, "value") else action,
                    "quantity": quantity,
                    "price": price,
                },
                source="backtest",
            )
            self.event_bus.publish(fill_event)

            # Notify strategy
            self.strategy.on_fill(fill_event)

    def _calculate_results(self) -> Dict:
        """
        Calculate backtest results

        Returns:
            Dictionary with results
        """
        # Get portfolio statistics
        portfolio_stats = self.portfolio.get_statistics(self._current_prices)

        # Calculate performance metrics
        metrics = PerformanceMetrics.calculate_all_metrics(
            equity_curve=self.portfolio.equity_curve,
            trades=self.portfolio.trades,
            initial_capital=self.initial_capital,
        )

        # Combine results
        results = {
            "portfolio": portfolio_stats,
            "metrics": metrics,
            "equity_curve": self.portfolio.equity_curve,
            "trades": self.portfolio.trades,
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "realized_pnl": pos.realized_pnl,
                    "unrealized_pnl": pos.unrealized_pnl,
                }
                for symbol, pos in self.portfolio.positions.items()
                if pos.quantity != 0
            },
        }

        return results

    def print_results(self, results: Dict) -> None:
        """
        Print backtest results

        Args:
            results: Results dictionary
        """
        # Print metrics
        PerformanceMetrics.print_metrics(results["metrics"])

        # Print portfolio summary
        print("PORTFOLIO SUMMARY")
        print("=" * 60)
        portfolio = results["portfolio"]
        print(f"Initial Capital:     ${portfolio['initial_capital']:,.2f}")
        print(f"Final Value:         ${portfolio['total_value']:,.2f}")
        print(f"Total P&L:           ${portfolio['total_pnl']:,.2f}")
        print(f"Total Return:        {portfolio['total_return']:.2%}")
        print(f"Cash Remaining:      ${portfolio['cash']:,.2f}")
        print(f"\nTotal Trades:        {portfolio['num_trades']}")
        print(f"Total Commission:    ${portfolio['total_commission']:,.2f}")
        print(f"Total Slippage:      ${portfolio['total_slippage']:,.2f}")
        print("=" * 60 + "\n")
