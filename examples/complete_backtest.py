"""
Complete Backtest Example

This example demonstrates a full end-to-end backtest using:
1. Yahoo Finance data provider
2. MA Crossover strategy
3. Backtesting engine
4. Performance metrics

Run this to see QuantX in action!
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger

from quantx.data.providers.yahoo import YahooFinanceProvider
from quantx.strategies import StrategyRegistry
from quantx.backtesting import BacktestEngine


def main():
    """Main function"""
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    print("\n" + "=" * 70)
    print(" " * 15 + "QuantX - Complete Backtest Example")
    print("=" * 70 + "\n")

    # 1. Set up data provider
    print("📊 Setting up data provider...")
    data_provider = YahooFinanceProvider(cache_enabled=True)
    print("✓ Yahoo Finance provider ready\n")

    # 2. Create strategy
    print("🎯 Creating MA Crossover strategy...")
    strategy_config = {
        "fast_period": 50,
        "slow_period": 200,
        "symbols": ["AAPL"],  # Trade Apple stock
    }

    strategy = StrategyRegistry.create("ma_crossover", strategy_config)
    print(f"✓ Strategy created: {strategy.name}")
    print(f"  - Fast MA: {strategy_config['fast_period']} days")
    print(f"  - Slow MA: {strategy_config['slow_period']} days")
    print(f"  - Symbols: {strategy_config['symbols']}\n")

    # 3. Set up backtest parameters
    print("⚙️  Configuring backtest...")
    initial_capital = 100000.0
    commission_rate = 0.001  # 0.1%
    slippage_rate = 0.0005  # 0.05%

    # Backtest period: Last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # ~2 years

    print(f"  - Initial Capital: ${initial_capital:,.2f}")
    print(f"  - Commission: {commission_rate:.2%}")
    print(f"  - Slippage: {slippage_rate:.2%}")
    print(f"  - Period: {start_date.date()} to {end_date.date()}\n")

    # 4. Create backtest engine
    print("🚀 Initializing backtest engine...")
    engine = BacktestEngine(
        strategy=strategy,
        data_provider=data_provider,
        initial_capital=initial_capital,
        commission_rate=commission_rate,
        slippage_rate=slippage_rate,
    )
    print("✓ Engine ready\n")

    # 5. Run backtest
    print("▶️  Running backtest...\n")
    results = engine.run(
        symbols=strategy_config["symbols"],
        start_date=start_date,
        end_date=end_date,
        interval="1d",
    )

    # 6. Display results
    print("\n📈 BACKTEST RESULTS")
    print("=" * 70 + "\n")

    engine.print_results(results)

    # 7. Display trades
    trades = results["trades"]
    if trades:
        print("\n📋 TRADE HISTORY (Last 10 trades)")
        print("=" * 70)
        print(
            f"{'Date':<12} {'Symbol':<8} {'Action':<6} {'Qty':<6} {'Price':<10} {'P&L':<12}"
        )
        print("-" * 70)

        for trade in trades[-10:]:  # Show last 10 trades
            print(
                f"{trade.timestamp.date()!s:<12} "
                f"{trade.symbol:<8} "
                f"{trade.action.upper():<6} "
                f"{trade.quantity:<6} "
                f"${trade.price:<9.2f} "
                f"${trade.pnl:>11.2f}"
            )
        print("=" * 70 + "\n")

    # 8. Save equity curve (optional)
    try:
        import matplotlib.pyplot as plt
        import pandas as pd

        print("📊 Generating equity curve plot...")

        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(
            results["equity_curve"], columns=["timestamp", "value"]
        )
        equity_df = equity_df.set_index("timestamp")

        # Create plot
        plt.figure(figsize=(12, 6))
        plt.plot(equity_df.index, equity_df["value"], linewidth=2)
        plt.axhline(
            y=initial_capital, color="r", linestyle="--", label="Initial Capital"
        )
        plt.title("Portfolio Equity Curve", fontsize=14, fontweight="bold")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save plot
        output_file = "equity_curve.png"
        plt.savefig(output_file, dpi=150)
        print(f"✓ Equity curve saved to: {output_file}\n")

    except ImportError:
        print("ℹ️  Install matplotlib to generate equity curve plot\n")

    # 9. Summary
    metrics = results["metrics"]
    print("🎯 SUMMARY")
    print("=" * 70)
    print(f"Total Return:        {metrics['total_return']:>8.2%}")
    print(f"Annual Return:       {metrics['annual_return']:>8.2%}")
    print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:>8.2f}")
    print(f"Max Drawdown:        {metrics['max_drawdown']:>8.2%}")
    print(f"Win Rate:            {metrics['win_rate']:>8.2%}")
    print(f"Total Trades:        {metrics['total_trades']:>8}")
    print("=" * 70 + "\n")

    print("✅ Backtest complete!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
