"""
Example: Feature Engineering Pipeline

This example demonstrates:
1. Creating individual feature calculators
2. Building a feature pipeline
3. Runtime configuration of features
4. Feature caching for performance
5. Feature store for persistence
6. Flexible feature selection

Run this to see the feature engineering in action!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from quantx.data.providers.yahoo import YahooFinanceProvider
from quantx.ml.features import (
    TechnicalFeatures,
    StatisticalFeatures,
    FeaturePipeline,
    FeatureStore
)


def example_1_basic_features():
    """Example 1: Calculate basic technical features"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Technical Features")
    print("=" * 70)
    
    # Fetch some data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print("\n📊 Fetching AAPL data...")
    data = provider.get_historical_data("AAPL", start_date, end_date, "1d")
    print(f"✓ Loaded {len(data)} days of data")
    
    # Create technical features calculator
    tech = TechnicalFeatures()
    
    print("\n🔧 Calculating technical features...")
    features = tech(data)
    
    print(f"✓ Generated {len(features.columns)} technical features")
    print(f"\nFeature names (first 10):")
    for i, col in enumerate(features.columns[:10], 1):
        print(f"  {i}. {col}")
    
    print(f"\n📈 Sample features (last 5 rows):")
    print(features[['sma_20', 'sma_50', 'rsi_14', 'macd']].tail())


def example_2_custom_configuration():
    """Example 2: Custom feature configuration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Custom Feature Configuration")
    print("=" * 70)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    data = provider.get_historical_data("GOOGL", start_date, end_date, "1d")
    
    print(f"\n📊 Loaded {len(data)} days of GOOGL data")
    
    # Create custom technical features
    # Only include specific indicators
    tech = TechnicalFeatures(
        ma_periods=[10, 20, 50],  # Only 3 MAs
        rsi_periods=[14],  # Only 1 RSI
        include_sma=True,
        include_ema=False,  # Disable EMA
        include_rsi=True,
        include_macd=True,
        include_bollinger=False,  # Disable Bollinger Bands
        include_atr=True,
        include_stochastic=False,  # Disable Stochastic
        include_cci=False,
        include_williams=False,
        include_adx=False,
        include_obv=True,
        include_vwap=True
    )
    
    features = tech(data)
    
    print(f"\n✓ Generated {len(features.columns)} custom features")
    print(f"\nEnabled features:")
    for col in sorted(features.columns):
        print(f"  - {col}")


def example_3_feature_pipeline():
    """Example 3: Combine multiple feature calculators"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Feature Pipeline")
    print("=" * 70)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    data = provider.get_historical_data("MSFT", start_date, end_date, "1d")
    
    print(f"\n📊 Loaded {len(data)} days of MSFT data")
    
    # Create pipeline with multiple calculators
    pipeline = FeaturePipeline([
        TechnicalFeatures(
            ma_periods=[20, 50],
            include_sma=True,
            include_rsi=True,
            include_macd=True
        ),
        StatisticalFeatures(
            return_periods=[1, 5, 10],
            rolling_windows=[20, 50],
            include_returns=True,
            include_volatility=True
        )
    ])
    
    print("\n🔧 Calculating features from pipeline...")
    features = pipeline.transform(data)
    
    print(f"✓ Pipeline generated {len(features.columns)} total features")
    print(f"\nFeature breakdown:")
    
    # Count features by type
    tech_features = [col for col in features.columns if any(
        x in col for x in ['sma', 'rsi', 'macd']
    )]
    stat_features = [col for col in features.columns if any(
        x in col for x in ['return', 'volatility', 'rolling']
    )]
    
    print(f"  Technical: {len(tech_features)}")
    print(f"  Statistical: {len(stat_features)}")
    
    print(f"\n📊 Sample combined features:")
    sample_cols = ['sma_20', 'rsi_14', 'return_1', 'volatility_20']
    available_cols = [col for col in sample_cols if col in features.columns]
    if available_cols:
        print(features[available_cols].tail())


def example_4_caching_performance():
    """Example 4: Feature caching for performance"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Feature Caching")
    print("=" * 70)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    data = provider.get_historical_data("AAPL", start_date, end_date, "1d")
    
    print(f"\n📊 Loaded {len(data)} days of data")
    
    # Create feature calculator
    tech = TechnicalFeatures()
    
    # First calculation (no cache)
    import time
    
    print("\n⏱️  First calculation (no cache)...")
    start = time.time()
    features1 = tech(data, use_cache=False)
    time1 = time.time() - start
    print(f"✓ Took {time1:.3f} seconds")
    
    # Second calculation (with cache)
    print("\n⏱️  Second calculation (with cache)...")
    start = time.time()
    features2 = tech(data, use_cache=True)
    time2 = time.time() - start
    print(f"✓ Took {time2:.3f} seconds")
    
    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"\n🚀 Speedup: {speedup:.1f}x faster with cache!")
    
    # Verify results are identical
    print(f"\n✓ Results identical: {features1.equals(features2)}")


def example_5_feature_store():
    """Example 5: Persist features to disk"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Feature Store (Persistence)")
    print("=" * 70)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    data = provider.get_historical_data("TSLA", start_date, end_date, "1d")
    
    print(f"\n📊 Loaded {len(data)} days of TSLA data")
    
    # Calculate features
    pipeline = FeaturePipeline([
        TechnicalFeatures(),
        StatisticalFeatures()
    ])
    
    features = pipeline.transform(data)
    print(f"✓ Calculated {len(features.columns)} features")
    
    # Create feature store (parquet backend)
    store = FeatureStore(backend="parquet", storage_path="./data/features")
    
    # Save features
    print("\n💾 Saving features to disk...")
    store.save("tsla_features_2024", features, metadata={
        "symbol": "TSLA",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "num_features": len(features.columns)
    })
    print("✓ Features saved")
    
    # Load features
    print("\n📂 Loading features from disk...")
    loaded_features = store.load("tsla_features_2024")
    print(f"✓ Loaded {len(loaded_features.columns)} features")
    
    # Verify
    print(f"\n✓ Data matches: {features.equals(loaded_features)}")


def example_6_runtime_reconfiguration():
    """Example 6: Change feature configuration at runtime"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Runtime Reconfiguration")
    print("=" * 70)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    data = provider.get_historical_data("NVDA", start_date, end_date, "1d")
    
    print(f"\n📊 Loaded {len(data)} days of NVDA data")
    
    # Configuration 1: Minimal features
    print("\n🔧 Configuration 1: Minimal features")
    pipeline1 = FeaturePipeline([
        TechnicalFeatures(
            ma_periods=[20],
            include_sma=True,
            include_ema=False,
            include_rsi=True,
            include_macd=False,
            include_bollinger=False,
            include_atr=False,
            include_stochastic=False
        )
    ])
    
    features1 = pipeline1.transform(data)
    print(f"✓ Generated {len(features1.columns)} features")
    
    # Configuration 2: Maximum features
    print("\n🔧 Configuration 2: Maximum features")
    pipeline2 = FeaturePipeline([
        TechnicalFeatures(),  # All indicators enabled
        StatisticalFeatures()  # All statistical features
    ])
    
    features2 = pipeline2.transform(data)
    print(f"✓ Generated {len(features2.columns)} features")
    
    print(f"\n📊 Comparison:")
    print(f"  Minimal config: {len(features1.columns)} features")
    print(f"  Maximum config: {len(features2.columns)} features")
    print(f"  Difference: {len(features2.columns) - len(features1.columns)} additional features")
    
    print("\n💡 You can switch between configurations at runtime!")
    print("   Perfect for A/B testing different feature sets.")


def main():
    """Run all examples"""
    print("\n")
    print("🚀 " * 35)
    print("QuantX Feature Engineering Examples")
    print("🚀 " * 35)
    
    try:
        example_1_basic_features()
        example_2_custom_configuration()
        example_3_feature_pipeline()
        example_4_caching_performance()
        example_5_feature_store()
        example_6_runtime_reconfiguration()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        print("""
Key Takeaways:
1. ✅ Feature calculators are highly configurable
2. ✅ Can enable/disable any feature at runtime
3. ✅ Pipeline combines multiple feature types
4. ✅ Automatic caching for performance
5. ✅ Persist features to disk
6. ✅ Switch configurations without code changes

🎯 This is the power of flexible architecture!
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
