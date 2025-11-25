"""
Strategy Registry Example

This example demonstrates:
1. Registering strategies
2. Listing available strategies
3. Creating strategy instances
4. Using the strategy registry
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quantx.strategies import StrategyRegistry
from loguru import logger


def main():
    """Main function"""
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    logger.info("=== QuantX Strategy Registry Example ===\n")

    # List registered strategies
    strategies = StrategyRegistry.list_strategies()
    logger.info("Registered strategies: {}\n", strategies)

    # Create MA Crossover strategy
    config = {
        "fast_period": 50,
        "slow_period": 200,
        "symbols": ["AAPL", "GOOGL"],
    }

    logger.info("Creating MA Crossover strategy with config:")
    logger.info("  Fast Period: {}", config["fast_period"])
    logger.info("  Slow Period: {}", config["slow_period"])
    logger.info("  Symbols: {}\n", config["symbols"])

    strategy = StrategyRegistry.create("ma_crossover", config)

    logger.info("Strategy created: {}", strategy.name)
    logger.info("Strategy type: {}", type(strategy).__name__)
    logger.info("Strategy config: {}\n", strategy.config)

    logger.info("=== Example Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
