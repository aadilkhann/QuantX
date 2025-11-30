"""
Technical Indicator Features

This module provides technical analysis indicators as features.

All indicators are configurable and can be enabled/disabled at runtime.

Supported Indicators:
- Trend: SMA, EMA, MACD, ADX
- Momentum: RSI, Stochastic, CCI, Williams %R
- Volatility: Bollinger Bands, ATR, Keltner Channels
- Volume: OBV, VWAP, MFI
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger

from quantx.ml.features.base import FeatureCalculator


class TechnicalFeatures(FeatureCalculator):
    """
    Calculate technical indicator features
    
    This calculator is highly flexible and configurable:
    - Enable/disable specific indicators
    - Configure periods for each indicator
    - Add custom indicators
    
    Example:
        # Use default configuration
        tech = TechnicalFeatures()
        
        # Custom configuration
        tech = TechnicalFeatures(
            ma_periods=[10, 20, 50],
            rsi_periods=[14],
            include_macd=True
        )
        
        features = tech(data)
    """
    
    def __init__(
        self,
        # Moving Average periods
        ma_periods: List[int] = [5, 10, 20, 50, 100, 200],
        
        # RSI periods
        rsi_periods: List[int] = [14, 21],
        
        # Bollinger Bands
        bb_periods: List[int] = [20],
        bb_std: List[float] = [2.0, 2.5],
        
        # MACD parameters
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        
        # ATR period
        atr_period: int = 14,
        
        # Stochastic parameters
        stoch_k_period: int = 14,
        stoch_d_period: int = 3,
        
        # CCI period
        cci_period: int = 20,
        
        # Williams %R period
        williams_period: int = 14,
        
        # ADX period
        adx_period: int = 14,
        
        # Enable/disable specific indicators
        include_sma: bool = True,
        include_ema: bool = True,
        include_rsi: bool = True,
        include_macd: bool = True,
        include_bollinger: bool = True,
        include_atr: bool = True,
        include_stochastic: bool = True,
        include_cci: bool = True,
        include_williams: bool = True,
        include_adx: bool = True,
        include_obv: bool = True,
        include_vwap: bool = True,
        
        **kwargs
    ):
        """Initialize technical features calculator"""
        super().__init__(
            name="TechnicalFeatures",
            description="Technical analysis indicators",
            ma_periods=ma_periods,
            rsi_periods=rsi_periods,
            bb_periods=bb_periods,
            bb_std=bb_std,
            **kwargs
        )
        
        self.ma_periods = ma_periods
        self.rsi_periods = rsi_periods
        self.bb_periods = bb_periods
        self.bb_std = bb_std
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.atr_period = atr_period
        self.stoch_k_period = stoch_k_period
        self.stoch_d_period = stoch_d_period
        self.cci_period = cci_period
        self.williams_period = williams_period
        self.adx_period = adx_period
        
        # Flags for which indicators to include
        self.include_sma = include_sma
        self.include_ema = include_ema
        self.include_rsi = include_rsi
        self.include_macd = include_macd
        self.include_bollinger = include_bollinger
        self.include_atr = include_atr
        self.include_stochastic = include_stochastic
        self.include_cci = include_cci
        self.include_williams = include_williams
        self.include_adx = include_adx
        self.include_obv = include_obv
        self.include_vwap = include_vwap
    
    def get_feature_type(self) -> str:
        return "technical"
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all enabled technical indicators"""
        features = pd.DataFrame(index=data.index)
        
        # Moving Averages
        if self.include_sma:
            for period in self.ma_periods:
                features[f'sma_{period}'] = self._sma(data['close'], period)
        
        if self.include_ema:
            for period in self.ma_periods:
                features[f'ema_{period}'] = self._ema(data['close'], period)
        
        # RSI
        if self.include_rsi:
            for period in self.rsi_periods:
                features[f'rsi_{period}'] = self._rsi(data['close'], period)
        
        # MACD
        if self.include_macd:
            macd, signal, hist = self._macd(
                data['close'],
                self.macd_fast,
                self.macd_slow,
                self.macd_signal
            )
            features['macd'] = macd
            features['macd_signal'] = signal
            features['macd_hist'] = hist
        
        # Bollinger Bands
        if self.include_bollinger:
            for period in self.bb_periods:
                for std in self.bb_std:
                    upper, middle, lower = self._bollinger_bands(
                        data['close'], period, std
                    )
                    features[f'bb_upper_{period}_{std}'] = upper
                    features[f'bb_middle_{period}_{std}'] = middle
                    features[f'bb_lower_{period}_{std}'] = lower
                    features[f'bb_width_{period}_{std}'] = (upper - lower) / middle
        
        # ATR
        if self.include_atr:
            features[f'atr_{self.atr_period}'] = self._atr(
                data['high'], data['low'], data['close'], self.atr_period
            )
        
        # Stochastic Oscillator
        if self.include_stochastic:
            k, d = self._stochastic(
                data['high'], data['low'], data['close'],
                self.stoch_k_period, self.stoch_d_period
            )
            features['stoch_k'] = k
            features['stoch_d'] = d
        
        # CCI
        if self.include_cci:
            features[f'cci_{self.cci_period}'] = self._cci(
                data['high'], data['low'], data['close'], self.cci_period
            )
        
        # Williams %R
        if self.include_williams:
            features[f'williams_{self.williams_period}'] = self._williams_r(
                data['high'], data['low'], data['close'], self.williams_period
            )
        
        # ADX
        if self.include_adx:
            features[f'adx_{self.adx_period}'] = self._adx(
                data['high'], data['low'], data['close'], self.adx_period
            )
        
        # OBV
        if self.include_obv:
            features['obv'] = self._obv(data['close'], data['volume'])
        
        # VWAP
        if self.include_vwap:
            features['vwap'] = self._vwap(
                data['high'], data['low'], data['close'], data['volume']
            )
        
        return features
    
    # ========================================================================
    # Indicator Implementations
    # ========================================================================
    
    @staticmethod
    def _sma(series: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return series.rolling(window=period).mean()
    
    @staticmethod
    def _ema(series: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _macd(
        series: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> tuple:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    @staticmethod
    def _bollinger_bands(
        series: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> tuple:
        """Bollinger Bands"""
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    @staticmethod
    def _atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def _stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> tuple:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    @staticmethod
    def _cci(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 20
    ) -> pd.Series:
        """Commodity Channel Index"""
        tp = (high + low + close) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean()
        )
        
        cci = (tp - sma) / (0.015 * mad)
        return cci
    
    @staticmethod
    def _williams_r(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Williams %R"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        williams = -100 * (highest_high - close) / (highest_high - lowest_low)
        return williams
    
    @staticmethod
    def _adx(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Average Directional Index"""
        # Calculate +DM and -DM
        high_diff = high.diff()
        low_diff = -low.diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # Calculate TR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Smooth +DM, -DM, and TR
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def _vwap(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap


# ============================================================================
# Convenience function for quick usage
# ============================================================================

def calculate_technical_features(
    data: pd.DataFrame,
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Quick function to calculate technical features
    
    Args:
        data: OHLCV DataFrame
        config: Optional configuration dict
        
    Returns:
        DataFrame with technical features
    """
    calculator = TechnicalFeatures(**(config or {}))
    return calculator(data)
