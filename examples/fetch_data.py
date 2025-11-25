"""
Simple Example: Fetch and Display Market Data

This example demonstrates:
1. Loading configuration
2. Creating a data provider
3. Fetching historical data
4. Displaying the data
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quantx.core.config import Config
from quantx.data.providers.yahoo import YahooFinanceProvider
from loguru import logger


def main():
    """Main function"""
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    logger.info("=== QuantX Data Fetching Example ===\n")

    # Load configuration
    config = Config()
    logger.info("Configuration loaded for environment: {}\n", config.app.env)

    # Create data provider
    provider = YahooFinanceProvider(cache_enabled=True)
    logger.info("Yahoo Finance provider initialized\n")

    # Define parameters
    symbol = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    logger.info("Fetching data for {}...", symbol)
    logger.info("Period: {} to {}\n", start_date.date(), end_date.date())

    # Fetch historical data
    try:
        data = provider.get_historical_data(symbol, start_date, end_date, interval="1d")

        logger.info("Successfully fetched {} rows\n", len(data))

        # Display first few rows
        logger.info("First 5 rows:")
        print(data.head())

        # Display statistics
        logger.info("\nData Statistics:")
        print(data.describe())

        # Display latest price
        latest = data.iloc[-1]
        logger.info("\nLatest Close Price: ${:.2f}", latest["close"])
        logger.info("Latest Volume: {:,}", int(latest["volume"]))

    except Exception as e:
        logger.error("Error fetching data: {}", e)
        return 1

    logger.info("\n=== Example Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
