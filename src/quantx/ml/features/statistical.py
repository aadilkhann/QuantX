"""
Statistical Features

This module provides statistical features for time series data.

Features include:
- Returns (simple, log, percentage)
- Rolling statistics (mean, std, skewness, kurtosis)
- Autocorrelation
- Volatility measures
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from scipy import stats
from loguru import logger

from quantx.ml.features.base import FeatureCalculator


class StatisticalFeatures(FeatureCalculator):
    """
    Calculate statistical features from price data
    
    All features are configurable and can be enabled/disabled at runtime.
    
    Example:
        # Default configuration
        stat = StatisticalFeatures()
        
        # Custom configuration
        stat = StatisticalFeatures(
            return_periods=[1, 5, 10],
            rolling_windows=[20, 50],
            include_skewness=True
        )
        
        features = stat(data)
    """
    
    def __init__(
        self,
        # Return calculation periods
        return_periods: List[int] = [1, 5, 10, 20],
        
        # Rolling window sizes
        rolling_windows: List[int] = [5, 10, 20, 50],
        
        # Autocorrelation lags
        autocorr_lags: List[int] = [1, 5, 10],
        
        # Enable/disable specific features
        include_returns: bool = True,
        include_log_returns: bool = True,
        include_rolling_mean: bool = True,
        include_rolling_std: bool = True,
        include_rolling_min: bool = True,
        include_rolling_max: bool = True,
        include_skewness: bool = True,
        include_kurtosis: bool = True,
        include_autocorr: bool = True,
        include_volatility: bool = True,
        include_momentum: bool = True,
        
        **kwargs
    ):
        """Initialize statistical features calculator"""
        super().__init__(
            name="StatisticalFeatures",
            description="Statistical features from price data",
            return_periods=return_periods,
            rolling_windows=rolling_windows,
            **kwargs
        )
        
        self.return_periods = return_periods
        self.rolling_windows = rolling_windows
        self.autocorr_lags = autocorr_lags
        
        # Feature flags
        self.include_returns = include_returns
        self.include_log_returns = include_log_returns
        self.include_rolling_mean = include_rolling_mean
        self.include_rolling_std = include_rolling_std
        self.include_rolling_min = include_rolling_min
        self.include_rolling_max = include_rolling_max
        self.include_skewness = include_skewness
        self.include_kurtosis = include_kurtosis
        self.include_autocorr = include_autocorr
        self.include_volatility = include_volatility
        self.include_momentum = include_momentum
    
    def get_feature_type(self) -> str:
        return "statistical"
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all enabled statistical features"""
        features = pd.DataFrame(index=data.index)
        close = data['close']
        
        # Returns
        if self.include_returns:
            for period in self.return_periods:
                features[f'return_{period}'] = close.pct_change(period)
        
        # Log Returns
        if self.include_log_returns:
            for period in self.return_periods:
                features[f'log_return_{period}'] = np.log(close / close.shift(period))
        
        # Rolling Statistics
        for window in self.rolling_windows:
            if self.include_rolling_mean:
                features[f'rolling_mean_{window}'] = close.rolling(window).mean()
            
            if self.include_rolling_std:
                features[f'rolling_std_{window}'] = close.rolling(window).std()
            
            if self.include_rolling_min:
                features[f'rolling_min_{window}'] = close.rolling(window).min()
            
            if self.include_rolling_max:
                features[f'rolling_max_{window}'] = close.rolling(window).max()
            
            if self.include_skewness:
                features[f'rolling_skew_{window}'] = close.rolling(window).skew()
            
            if self.include_kurtosis:
                features[f'rolling_kurt_{window}'] = close.rolling(window).kurt()
        
        # Autocorrelation
        if self.include_autocorr:
            returns = close.pct_change()
            for lag in self.autocorr_lags:
                features[f'autocorr_{lag}'] = returns.rolling(20).apply(
                    lambda x: x.autocorr(lag=lag) if len(x) > lag else np.nan
                )
        
        # Volatility measures
        if self.include_volatility:
            returns = close.pct_change()
            for window in self.rolling_windows:
                # Historical volatility (annualized)
                features[f'volatility_{window}'] = (
                    returns.rolling(window).std() * np.sqrt(252)
                )
                
                # Parkinson volatility (uses high-low)
                if 'high' in data.columns and 'low' in data.columns:
                    hl_ratio = np.log(data['high'] / data['low'])
                    features[f'parkinson_vol_{window}'] = (
                        np.sqrt(hl_ratio.rolling(window).var() / (4 * np.log(2))) * np.sqrt(252)
                    )
        
        # Momentum features
        if self.include_momentum:
            for window in self.rolling_windows:
                # Rate of change
                features[f'roc_{window}'] = (
                    (close - close.shift(window)) / close.shift(window) * 100
                )
                
                # Momentum
                features[f'momentum_{window}'] = close - close.shift(window)
        
        # Price position in range
        for window in self.rolling_windows:
            rolling_min = close.rolling(window).min()
            rolling_max = close.rolling(window).max()
            features[f'price_position_{window}'] = (
                (close - rolling_min) / (rolling_max - rolling_min)
            )
        
        # Distance from moving average
        for window in self.rolling_windows:
            ma = close.rolling(window).mean()
            features[f'distance_from_ma_{window}'] = (close - ma) / ma
        
        return features


# ============================================================================
# Convenience function
# ============================================================================

def calculate_statistical_features(
    data: pd.DataFrame,
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Quick function to calculate statistical features
    
    Args:
        data: OHLCV DataFrame
        config: Optional configuration dict
        
    Returns:
        DataFrame with statistical features
    """
    calculator = StatisticalFeatures(**(config or {}))
    return calculator(data)
