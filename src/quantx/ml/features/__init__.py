"""
QuantX ML Features Module

Flexible, pluggable feature engineering for trading strategies.

Usage:
    from quantx.ml.features import (
        TechnicalFeatures,
        StatisticalFeatures,
        FeaturePipeline
    )
    
    # Create pipeline
    pipeline = FeaturePipeline([
        TechnicalFeatures(),
        StatisticalFeatures()
    ])
    
    # Calculate features
    features = pipeline.transform(data)
"""

from quantx.ml.features.base import (
    FeatureCalculator,
    FeaturePipeline,
    FeatureStore,
    FeatureMetadata,
    create_feature_pipeline
)

from quantx.ml.features.technical import (
    TechnicalFeatures,
    calculate_technical_features
)

from quantx.ml.features.statistical import (
    StatisticalFeatures,
    calculate_statistical_features
)

__all__ = [
    # Base classes
    "FeatureCalculator",
    "FeaturePipeline",
    "FeatureStore",
    "FeatureMetadata",
    "create_feature_pipeline",
    
    # Feature calculators
    "TechnicalFeatures",
    "StatisticalFeatures",
    
    # Convenience functions
    "calculate_technical_features",
    "calculate_statistical_features",
]
