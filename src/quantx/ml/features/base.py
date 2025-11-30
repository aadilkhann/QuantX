"""
Base Feature Engineering Framework

This module provides the foundation for flexible, pluggable feature engineering.

Key Features:
- Abstract base classes for feature calculators
- Feature pipeline composition
- Automatic caching for performance
- Feature metadata and validation
- Runtime feature selection
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import hashlib
import pickle
from loguru import logger


# ============================================================================
# Feature Metadata
# ============================================================================

@dataclass
class FeatureMetadata:
    """Metadata for a calculated feature"""
    name: str
    description: str
    feature_type: str  # "technical", "statistical", "sentiment", etc.
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "feature_type": self.feature_type,
            "dependencies": self.dependencies,
            "parameters": self.parameters,
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }


# ============================================================================
# Base Feature Calculator
# ============================================================================

class FeatureCalculator(ABC):
    """
    Abstract base class for feature calculators
    
    All feature calculators must inherit from this class and implement
    the calculate() method.
    
    Features:
    - Automatic caching
    - Metadata tracking
    - Validation
    - Dependency management
    """
    
    def __init__(self, name: str, description: str = "", **params):
        """
        Initialize feature calculator
        
        Args:
            name: Feature name
            description: Feature description
            **params: Feature-specific parameters
        """
        self.name = name
        self.description = description
        self.params = params
        self.metadata = FeatureMetadata(
            name=name,
            description=description,
            feature_type=self.get_feature_type(),
            parameters=params
        )
        self._cache: Dict[str, pd.DataFrame] = {}
        self._cache_enabled = True
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate features from input data
        
        Args:
            data: Input DataFrame with OHLCV data
            
        Returns:
            DataFrame with calculated features
        """
        pass
    
    @abstractmethod
    def get_feature_type(self) -> str:
        """Return feature type (technical, statistical, etc.)"""
        pass
    
    def get_required_columns(self) -> List[str]:
        """
        Return list of required columns in input data
        
        Override this method to specify required columns
        """
        return ["open", "high", "low", "close", "volume"]
    
    def validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate input data
        
        Args:
            data: Input DataFrame
            
        Raises:
            ValueError: If data is invalid
        """
        required_cols = self.get_required_columns()
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise ValueError(
                f"Missing required columns for {self.name}: {missing_cols}"
            )
        
        if len(data) == 0:
            raise ValueError(f"Empty DataFrame provided to {self.name}")
    
    def __call__(self, data: pd.DataFrame, use_cache: bool = True) -> pd.DataFrame:
        """
        Calculate features with caching support
        
        Args:
            data: Input DataFrame
            use_cache: Whether to use cached results
            
        Returns:
            DataFrame with calculated features
        """
        # Validate input
        self.validate_data(data)
        
        # Check cache
        if use_cache and self._cache_enabled:
            cache_key = self._get_cache_key(data)
            if cache_key in self._cache:
                logger.debug(f"Using cached features for {self.name}")
                return self._cache[cache_key]
        
        # Calculate features
        logger.debug(f"Calculating features: {self.name}")
        features = self.calculate(data)
        
        # Validate output
        self._validate_output(features)
        
        # Cache results
        if self._cache_enabled:
            cache_key = self._get_cache_key(data)
            self._cache[cache_key] = features
        
        return features
    
    def _get_cache_key(self, data: pd.DataFrame) -> str:
        """Generate cache key from data"""
        # Use hash of data shape, columns, and first/last values
        key_parts = [
            str(data.shape),
            str(sorted(data.columns.tolist())),
            str(data.index[0]) if len(data) > 0 else "",
            str(data.index[-1]) if len(data) > 0 else "",
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _validate_output(self, features: pd.DataFrame) -> None:
        """Validate calculated features"""
        if not isinstance(features, pd.DataFrame):
            raise TypeError(
                f"{self.name} must return pd.DataFrame, got {type(features)}"
            )
        
        # Check for infinite values
        if features.isin([np.inf, -np.inf]).any().any():
            logger.warning(f"{self.name} produced infinite values")
        
        # Check for NaN values
        nan_count = features.isna().sum().sum()
        if nan_count > 0:
            logger.debug(f"{self.name} produced {nan_count} NaN values")
    
    def clear_cache(self) -> None:
        """Clear cached features"""
        self._cache.clear()
        logger.debug(f"Cleared cache for {self.name}")
    
    def enable_cache(self) -> None:
        """Enable caching"""
        self._cache_enabled = True
    
    def disable_cache(self) -> None:
        """Disable caching"""
        self._cache_enabled = False
        self.clear_cache()
    
    def get_metadata(self) -> FeatureMetadata:
        """Get feature metadata"""
        return self.metadata
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


# ============================================================================
# Feature Pipeline
# ============================================================================

class FeaturePipeline:
    """
    Compose multiple feature calculators into a pipeline
    
    Features:
    - Sequential feature calculation
    - Parallel execution support
    - Feature selection
    - Caching
    
    Example:
        pipeline = FeaturePipeline([
            TechnicalFeatures(),
            StatisticalFeatures(),
            SentimentFeatures()
        ])
        
        features = pipeline.transform(data)
    """
    
    def __init__(
        self,
        calculators: List[FeatureCalculator],
        feature_selection: Optional[Callable] = None,
        n_jobs: int = 1
    ):
        """
        Initialize feature pipeline
        
        Args:
            calculators: List of feature calculators
            feature_selection: Optional feature selection function
            n_jobs: Number of parallel jobs (1 = sequential)
        """
        self.calculators = calculators
        self.feature_selection = feature_selection
        self.n_jobs = n_jobs
        self._feature_names: List[str] = []
    
    def transform(
        self,
        data: pd.DataFrame,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Transform data through feature pipeline
        
        Args:
            data: Input DataFrame
            use_cache: Whether to use cached features
            
        Returns:
            DataFrame with all calculated features
        """
        all_features = []
        
        # Calculate features from each calculator
        for calculator in self.calculators:
            try:
                features = calculator(data, use_cache=use_cache)
                all_features.append(features)
                logger.debug(
                    f"Calculated {len(features.columns)} features "
                    f"from {calculator.name}"
                )
            except Exception as e:
                logger.error(
                    f"Error calculating features from {calculator.name}: {e}"
                )
                continue
        
        if not all_features:
            raise ValueError("No features were calculated")
        
        # Combine all features
        combined_features = pd.concat(all_features, axis=1)
        
        # Remove duplicate columns
        combined_features = combined_features.loc[
            :, ~combined_features.columns.duplicated()
        ]
        
        # Apply feature selection if provided
        if self.feature_selection is not None:
            combined_features = self.feature_selection(combined_features)
        
        self._feature_names = combined_features.columns.tolist()
        
        logger.info(
            f"Pipeline produced {len(combined_features.columns)} features"
        )
        
        return combined_features
    
    def fit_transform(
        self,
        data: pd.DataFrame,
        target: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """
        Fit and transform (for compatibility with sklearn)
        
        Args:
            data: Input DataFrame
            target: Optional target variable
            
        Returns:
            Transformed features
        """
        return self.transform(data)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self._feature_names
    
    def get_feature_metadata(self) -> List[FeatureMetadata]:
        """Get metadata for all features"""
        return [calc.get_metadata() for calc in self.calculators]
    
    def clear_cache(self) -> None:
        """Clear cache for all calculators"""
        for calculator in self.calculators:
            calculator.clear_cache()
    
    def add_calculator(self, calculator: FeatureCalculator) -> None:
        """Add a new feature calculator to the pipeline"""
        self.calculators.append(calculator)
        logger.info(f"Added calculator: {calculator.name}")
    
    def remove_calculator(self, name: str) -> None:
        """Remove a feature calculator by name"""
        self.calculators = [
            calc for calc in self.calculators if calc.name != name
        ]
        logger.info(f"Removed calculator: {name}")
    
    def __len__(self) -> int:
        return len(self.calculators)
    
    def __repr__(self) -> str:
        calc_names = [calc.name for calc in self.calculators]
        return f"FeaturePipeline(calculators={calc_names})"


# ============================================================================
# Feature Store (for persistence)
# ============================================================================

class FeatureStore:
    """
    Store and retrieve calculated features
    
    Supports multiple backends:
    - Memory (dict)
    - Disk (pickle, parquet)
    - Database (future)
    """
    
    def __init__(self, backend: str = "memory", storage_path: Optional[Path] = None):
        """
        Initialize feature store
        
        Args:
            backend: Storage backend ("memory", "pickle", "parquet")
            storage_path: Path for disk-based storage
        """
        self.backend = backend
        self.storage_path = Path(storage_path) if storage_path else Path("./feature_store")
        self._memory_store: Dict[str, pd.DataFrame] = {}
        
        if backend in ["pickle", "parquet"]:
            self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, key: str, features: pd.DataFrame, metadata: Optional[Dict] = None) -> None:
        """
        Save features to store
        
        Args:
            key: Unique key for features
            features: Feature DataFrame
            metadata: Optional metadata
        """
        if self.backend == "memory":
            self._memory_store[key] = features
        
        elif self.backend == "pickle":
            file_path = self.storage_path / f"{key}.pkl"
            with open(file_path, 'wb') as f:
                pickle.dump({"features": features, "metadata": metadata}, f)
            logger.debug(f"Saved features to {file_path}")
        
        elif self.backend == "parquet":
            file_path = self.storage_path / f"{key}.parquet"
            features.to_parquet(file_path)
            
            # Save metadata separately
            if metadata:
                meta_path = self.storage_path / f"{key}_meta.pkl"
                with open(meta_path, 'wb') as f:
                    pickle.dump(metadata, f)
            
            logger.debug(f"Saved features to {file_path}")
    
    def load(self, key: str) -> Optional[pd.DataFrame]:
        """
        Load features from store
        
        Args:
            key: Unique key for features
            
        Returns:
            Feature DataFrame or None if not found
        """
        if self.backend == "memory":
            return self._memory_store.get(key)
        
        elif self.backend == "pickle":
            file_path = self.storage_path / f"{key}.pkl"
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                return data["features"]
            return None
        
        elif self.backend == "parquet":
            file_path = self.storage_path / f"{key}.parquet"
            if file_path.exists():
                return pd.read_parquet(file_path)
            return None
    
    def exists(self, key: str) -> bool:
        """Check if features exist in store"""
        if self.backend == "memory":
            return key in self._memory_store
        
        elif self.backend == "pickle":
            return (self.storage_path / f"{key}.pkl").exists()
        
        elif self.backend == "parquet":
            return (self.storage_path / f"{key}.parquet").exists()
        
        return False
    
    def delete(self, key: str) -> None:
        """Delete features from store"""
        if self.backend == "memory":
            self._memory_store.pop(key, None)
        
        elif self.backend == "pickle":
            file_path = self.storage_path / f"{key}.pkl"
            if file_path.exists():
                file_path.unlink()
        
        elif self.backend == "parquet":
            file_path = self.storage_path / f"{key}.parquet"
            if file_path.exists():
                file_path.unlink()
            
            meta_path = self.storage_path / f"{key}_meta.pkl"
            if meta_path.exists():
                meta_path.unlink()
    
    def clear(self) -> None:
        """Clear all features from store"""
        if self.backend == "memory":
            self._memory_store.clear()
        
        elif self.backend in ["pickle", "parquet"]:
            for file in self.storage_path.glob("*"):
                file.unlink()
        
        logger.info("Cleared feature store")


# ============================================================================
# Utility Functions
# ============================================================================

def create_feature_pipeline(
    feature_types: List[str],
    config: Optional[Dict[str, Any]] = None
) -> FeaturePipeline:
    """
    Create feature pipeline from configuration
    
    Args:
        feature_types: List of feature types to include
        config: Optional configuration dict
        
    Returns:
        Configured FeaturePipeline
    """
    from quantx.ml.features.technical import TechnicalFeatures
    from quantx.ml.features.statistical import StatisticalFeatures
    
    calculators = []
    
    if "technical" in feature_types:
        calculators.append(TechnicalFeatures(**(config or {}).get("technical", {})))
    
    if "statistical" in feature_types:
        calculators.append(StatisticalFeatures(**(config or {}).get("statistical", {})))
    
    # Add more feature types as they're implemented
    
    return FeaturePipeline(calculators)
