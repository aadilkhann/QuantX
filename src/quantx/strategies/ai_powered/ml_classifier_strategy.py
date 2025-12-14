"""
ML Classifier Strategy - Uses trained ML models for trading decisions.

This strategy loads a trained classification model and uses it to predict
market direction (buy/sell/hold) based on engineered features.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import pandas as pd
import numpy as np
from loguru import logger

from quantx.strategies.base import AIPoweredStrategy, Signal
from quantx.ml.features import FeaturePipeline, TechnicalFeatures, StatisticalFeatures
from quantx.ml.models import ModelFactory
from quantx.ml.models.base import BaseModel


class MLClassifierStrategy(AIPoweredStrategy):
    """
    Trading strategy that uses ML classifiers to predict market direction.
    
    This strategy:
    1. Generates features using a feature pipeline
    2. Uses a trained model to predict direction (1=buy, 0=hold, -1=sell)
    3. Generates trading signals based on predictions and confidence
    4. Supports configurable thresholds for signal generation
    
    Example:
        >>> strategy = MLClassifierStrategy(
        ...     name="xgb_classifier",
        ...     model_path="models/xgboost_model.pkl",
        ...     symbols=["AAPL"],
        ...     prediction_threshold=0.6
        ... )
        >>> strategy.on_start()
        >>> strategy.on_data(market_data)
    """
    
    def __init__(
        self,
        name: str = "ml_classifier",
        symbols: Optional[List[str]] = None,
        model_path: Optional[str] = None,
        model_type: str = "xgboost",
        prediction_threshold: float = 0.6,
        confidence_threshold: float = 0.7,
        position_size: float = 1000.0,
        use_probability: bool = True,
        feature_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize ML Classifier Strategy.
        
        Args:
            name: Strategy name
            symbols: List of symbols to trade
            model_path: Path to trained model file
            model_type: Type of model (xgboost, lightgbm, random_forest)
            prediction_threshold: Minimum probability for buy/sell (0.5-1.0)
            confidence_threshold: Minimum confidence for high-conviction trades
            position_size: Base position size in dollars
            use_probability: Use probability predictions vs hard predictions
            feature_config: Configuration for feature engineering
            **kwargs: Additional strategy parameters
        """
        super().__init__(name=name, symbols=symbols, **kwargs)
        
        self.model_path = model_path
        self.model_type = model_type
        self.prediction_threshold = prediction_threshold
        self.confidence_threshold = confidence_threshold
        self.position_size = position_size
        self.use_probability = use_probability
        self.feature_config = feature_config or {}
        
        # Model and features
        self.model: Optional[BaseModel] = None
        self.feature_pipeline: Optional[FeaturePipeline] = None
        
        # State tracking
        self.last_prediction: Dict[str, float] = {}
        self.prediction_history: Dict[str, List[float]] = {}
        
        logger.info(f"Initialized {self.name} with threshold={prediction_threshold}")
    
    def on_start(self) -> None:
        """Initialize model and feature pipeline."""
        super().on_start()
        
        # Load model
        if self.model_path:
            self._load_model()
        else:
            logger.warning(f"{self.name}: No model path provided, model must be set manually")
        
        # Create feature pipeline
        self._create_feature_pipeline()
        
        # Initialize prediction history
        for symbol in self.symbols:
            self.prediction_history[symbol] = []
        
        logger.info(f"{self.name} started successfully")
    
    def _load_model(self) -> None:
        """Load trained model from disk."""
        try:
            model_path = Path(self.model_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            # Load model using factory
            self.model = ModelFactory.load_model(str(model_path))
            logger.info(f"Loaded model from {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _create_feature_pipeline(self) -> None:
        """Create feature engineering pipeline."""
        # Get feature config
        tech_config = self.feature_config.get("technical", {})
        stat_config = self.feature_config.get("statistical", {})
        
        # Create calculators
        calculators = []
        
        # Technical features
        if tech_config.get("enabled", True):
            calculators.append(TechnicalFeatures(
                ma_periods=tech_config.get("ma_periods", [10, 20, 50]),
                include_rsi=tech_config.get("include_rsi", True),
                include_macd=tech_config.get("include_macd", True),
                include_bollinger=tech_config.get("include_bollinger", True),
                include_atr=tech_config.get("include_atr", True)
            ))
        
        # Statistical features
        if stat_config.get("enabled", True):
            calculators.append(StatisticalFeatures(
                return_periods=stat_config.get("return_periods", [1, 5, 10]),
                rolling_windows=stat_config.get("rolling_windows", [20, 50]),
                include_volatility=stat_config.get("include_volatility", True)
            ))
        
        # Create pipeline
        self.feature_pipeline = FeaturePipeline(calculators)
        logger.info(f"Created feature pipeline with {len(calculators)} calculators")
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for model prediction.
        
        Args:
            data: Market data (OHLCV)
            
        Returns:
            DataFrame with engineered features
        """
        if self.feature_pipeline is None:
            raise ValueError("Feature pipeline not initialized")
        
        # Generate features
        features = self.feature_pipeline.transform(data)
        
        # Drop NaN values (from indicators)
        features = features.dropna()
        
        return features
    
    def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate prediction from features.
        
        Args:
            features: Engineered features
            
        Returns:
            Dictionary with prediction, probability, and confidence
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        if len(features) == 0:
            return {"prediction": 0, "probability": 0.5, "confidence": 0.0}
        
        # Get latest features
        X = features.iloc[[-1]]
        
        # Get prediction
        if self.use_probability:
            # Get probability predictions
            probabilities = self.model.predict_proba(X)
            
            # Assuming binary classification: [prob_sell, prob_buy]
            # or multi-class: [prob_sell, prob_hold, prob_buy]
            if probabilities.shape[1] == 2:
                prob_buy = probabilities[0, 1]
                prob_sell = probabilities[0, 0]
                
                # Determine prediction
                if prob_buy > self.prediction_threshold:
                    prediction = 1  # Buy
                    confidence = prob_buy
                elif prob_sell > self.prediction_threshold:
                    prediction = -1  # Sell
                    confidence = prob_sell
                else:
                    prediction = 0  # Hold
                    confidence = max(prob_buy, prob_sell)
                
                return {
                    "prediction": prediction,
                    "probability": prob_buy,
                    "confidence": confidence,
                    "prob_buy": prob_buy,
                    "prob_sell": prob_sell
                }
            else:
                # Multi-class
                prob_sell = probabilities[0, 0]
                prob_hold = probabilities[0, 1]
                prob_buy = probabilities[0, 2]
                
                max_prob = max(prob_sell, prob_hold, prob_buy)
                
                if prob_buy == max_prob and prob_buy > self.prediction_threshold:
                    prediction = 1
                elif prob_sell == max_prob and prob_sell > self.prediction_threshold:
                    prediction = -1
                else:
                    prediction = 0
                
                return {
                    "prediction": prediction,
                    "probability": prob_buy,
                    "confidence": max_prob,
                    "prob_buy": prob_buy,
                    "prob_hold": prob_hold,
                    "prob_sell": prob_sell
                }
        else:
            # Hard prediction
            prediction = self.model.predict(X)[0]
            return {
                "prediction": int(prediction),
                "probability": 0.5,
                "confidence": 1.0
            }
    
    def on_data(self, data: pd.DataFrame) -> None:
        """
        Process market data and generate signals.
        
        Args:
            data: Market data with OHLCV columns
        """
        if self.model is None:
            logger.warning(f"{self.name}: Model not loaded, skipping signal generation")
            return
        
        try:
            # Prepare features
            features = self.prepare_features(data)
            
            if len(features) == 0:
                logger.debug(f"{self.name}: Not enough data for features")
                return
            
            # Get prediction
            result = self.predict(features)
            prediction = result["prediction"]
            confidence = result["confidence"]
            
            # Get current symbol (assume single symbol for now)
            symbol = self.symbols[0] if self.symbols else "UNKNOWN"
            
            # Store prediction
            self.last_prediction[symbol] = result["probability"]
            self.prediction_history[symbol].append(result["probability"])
            
            # Get current price
            current_price = data["close"].iloc[-1]
            
            # Generate signals based on prediction
            if prediction == 1:  # Buy signal
                if not self.has_position(symbol):
                    # Calculate position size (can be adjusted by confidence)
                    size = self.position_size
                    if confidence > self.confidence_threshold:
                        size *= 1.5  # Increase size for high confidence
                    
                    signal = self.buy(
                        symbol=symbol,
                        quantity=int(size / current_price),
                        price=current_price,
                        metadata={
                            "prediction": prediction,
                            "confidence": confidence,
                            "probability": result["probability"]
                        }
                    )
                    logger.info(
                        f"{self.name}: BUY signal for {symbol} at {current_price:.2f} "
                        f"(confidence={confidence:.3f})"
                    )
            
            elif prediction == -1:  # Sell signal
                if self.has_position(symbol):
                    signal = self.sell(
                        symbol=symbol,
                        quantity=self.get_position_size(symbol),
                        price=current_price,
                        metadata={
                            "prediction": prediction,
                            "confidence": confidence,
                            "probability": result["probability"]
                        }
                    )
                    logger.info(
                        f"{self.name}: SELL signal for {symbol} at {current_price:.2f} "
                        f"(confidence={confidence:.3f})"
                    )
            
            else:  # Hold
                logger.debug(
                    f"{self.name}: HOLD for {symbol} "
                    f"(prob={result['probability']:.3f}, threshold={self.prediction_threshold})"
                )
        
        except Exception as e:
            logger.error(f"{self.name}: Error processing data: {e}")
    
    def get_prediction_stats(self, symbol: str) -> Dict[str, float]:
        """
        Get prediction statistics for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with prediction statistics
        """
        if symbol not in self.prediction_history:
            return {}
        
        history = self.prediction_history[symbol]
        if len(history) == 0:
            return {}
        
        return {
            "mean_probability": np.mean(history),
            "std_probability": np.std(history),
            "min_probability": np.min(history),
            "max_probability": np.max(history),
            "last_probability": history[-1],
            "num_predictions": len(history)
        }
    
    def set_model(self, model: BaseModel) -> None:
        """
        Set model manually (useful for testing).
        
        Args:
            model: Trained model instance
        """
        self.model = model
        logger.info(f"Model set manually: {type(model).__name__}")
