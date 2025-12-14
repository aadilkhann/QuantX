"""
Signal Strength Strategy - Uses prediction confidence for position sizing.

This strategy uses ML model prediction confidence to determine position sizes,
allowing for more aggressive positions when the model is highly confident.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from loguru import logger

from quantx.strategies.ai_powered.ml_classifier_strategy import MLClassifierStrategy
from quantx.ml.models.base import BaseModel


class SignalStrengthStrategy(MLClassifierStrategy):
    """
    Advanced ML strategy that adjusts position sizes based on prediction confidence.
    
    This strategy extends MLClassifierStrategy by:
    1. Using prediction confidence to scale position sizes
    2. Supporting multiple confidence tiers
    3. Implementing dynamic risk management
    4. Allowing ensemble model predictions
    
    Example:
        >>> strategy = SignalStrengthStrategy(
        ...     name="confidence_trader",
        ...     model_path="models/xgboost_model.pkl",
        ...     symbols=["AAPL"],
        ...     confidence_tiers={
        ...         0.9: 2.0,  # 2x position at 90% confidence
        ...         0.8: 1.5,  # 1.5x position at 80% confidence
        ...         0.7: 1.0,  # 1x position at 70% confidence
        ...     }
        ... )
    """
    
    def __init__(
        self,
        name: str = "signal_strength",
        symbols: Optional[List[str]] = None,
        model_path: Optional[str] = None,
        model_type: str = "xgboost",
        prediction_threshold: float = 0.6,
        min_confidence: float = 0.65,
        max_confidence: float = 0.95,
        base_position_size: float = 1000.0,
        confidence_tiers: Optional[Dict[float, float]] = None,
        max_position_multiplier: float = 3.0,
        use_ensemble: bool = False,
        ensemble_models: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize Signal Strength Strategy.
        
        Args:
            name: Strategy name
            symbols: List of symbols to trade
            model_path: Path to trained model file
            model_type: Type of model
            prediction_threshold: Minimum probability for signals
            min_confidence: Minimum confidence to trade (below this = no trade)
            max_confidence: Maximum confidence (for scaling)
            base_position_size: Base position size in dollars
            confidence_tiers: Dict mapping confidence levels to position multipliers
            max_position_multiplier: Maximum position size multiplier
            use_ensemble: Use multiple models for ensemble predictions
            ensemble_models: List of model paths for ensemble
            **kwargs: Additional parameters
        """
        super().__init__(
            name=name,
            symbols=symbols,
            model_path=model_path,
            model_type=model_type,
            prediction_threshold=prediction_threshold,
            position_size=base_position_size,
            **kwargs
        )
        
        self.min_confidence = min_confidence
        self.max_confidence = max_confidence
        self.base_position_size = base_position_size
        self.max_position_multiplier = max_position_multiplier
        self.use_ensemble = use_ensemble
        self.ensemble_models_paths = ensemble_models or []
        
        # Default confidence tiers if not provided
        self.confidence_tiers = confidence_tiers or {
            0.95: 3.0,  # Very high confidence: 3x position
            0.85: 2.0,  # High confidence: 2x position
            0.75: 1.5,  # Medium-high confidence: 1.5x position
            0.65: 1.0,  # Medium confidence: 1x position
        }
        
        # Ensemble models
        self.ensemble_models: List[BaseModel] = []
        
        # Statistics
        self.position_sizes_history: Dict[str, List[float]] = {}
        self.confidence_history: Dict[str, List[float]] = {}
        
        logger.info(
            f"Initialized {self.name} with confidence tiers: {self.confidence_tiers}"
        )
    
    def on_start(self) -> None:
        """Initialize models and feature pipeline."""
        super().on_start()
        
        # Load ensemble models if enabled
        if self.use_ensemble and self.ensemble_models_paths:
            self._load_ensemble_models()
        
        # Initialize history
        for symbol in self.symbols:
            self.position_sizes_history[symbol] = []
            self.confidence_history[symbol] = []
    
    def _load_ensemble_models(self) -> None:
        """Load multiple models for ensemble predictions."""
        from quantx.ml.models import ModelFactory
        from pathlib import Path
        
        for model_path in self.ensemble_models_paths:
            try:
                path = Path(model_path)
                if path.exists():
                    model = ModelFactory.load_model(str(path))
                    self.ensemble_models.append(model)
                    logger.info(f"Loaded ensemble model from {model_path}")
                else:
                    logger.warning(f"Ensemble model not found: {model_path}")
            except Exception as e:
                logger.error(f"Failed to load ensemble model {model_path}: {e}")
        
        logger.info(f"Loaded {len(self.ensemble_models)} ensemble models")
    
    def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate prediction with ensemble support.
        
        Args:
            features: Engineered features
            
        Returns:
            Dictionary with prediction, probability, and confidence
        """
        if not self.use_ensemble or len(self.ensemble_models) == 0:
            # Use single model prediction
            return super().predict(features)
        
        # Ensemble prediction: average probabilities from all models
        all_predictions = []
        all_probabilities = []
        
        # Get prediction from main model
        main_result = super().predict(features)
        all_predictions.append(main_result["prediction"])
        all_probabilities.append(main_result.get("prob_buy", 0.5))
        
        # Get predictions from ensemble models
        X = features.iloc[[-1]]
        for model in self.ensemble_models:
            try:
                proba = model.predict_proba(X)
                if proba.shape[1] == 2:
                    prob_buy = proba[0, 1]
                else:
                    prob_buy = proba[0, 2]  # Multi-class
                
                all_probabilities.append(prob_buy)
                
                # Determine prediction
                if prob_buy > self.prediction_threshold:
                    all_predictions.append(1)
                elif prob_buy < (1 - self.prediction_threshold):
                    all_predictions.append(-1)
                else:
                    all_predictions.append(0)
            
            except Exception as e:
                logger.error(f"Ensemble model prediction failed: {e}")
        
        # Average predictions
        avg_probability = np.mean(all_probabilities)
        prediction_mode = int(np.median(all_predictions))  # Use median for robustness
        
        # Calculate confidence based on agreement
        agreement = np.mean([p == prediction_mode for p in all_predictions])
        confidence = avg_probability * agreement  # Penalize disagreement
        
        return {
            "prediction": prediction_mode,
            "probability": avg_probability,
            "confidence": confidence,
            "ensemble_size": len(all_predictions),
            "agreement": agreement
        }
    
    def calculate_position_size(
        self,
        symbol: str,
        confidence: float,
        current_price: float
    ) -> int:
        """
        Calculate position size based on confidence level.
        
        Args:
            symbol: Trading symbol
            confidence: Prediction confidence (0-1)
            current_price: Current market price
            
        Returns:
            Position size in shares
        """
        # Check minimum confidence
        if confidence < self.min_confidence:
            logger.debug(
                f"{self.name}: Confidence {confidence:.3f} below minimum "
                f"{self.min_confidence}, no trade"
            )
            return 0
        
        # Find appropriate tier
        multiplier = 1.0
        for tier_confidence, tier_multiplier in sorted(
            self.confidence_tiers.items(), reverse=True
        ):
            if confidence >= tier_confidence:
                multiplier = tier_multiplier
                break
        
        # Cap multiplier
        multiplier = min(multiplier, self.max_position_multiplier)
        
        # Calculate position size
        position_value = self.base_position_size * multiplier
        shares = int(position_value / current_price)
        
        logger.debug(
            f"{self.name}: Confidence={confidence:.3f}, Multiplier={multiplier:.2f}, "
            f"Shares={shares}"
        )
        
        return shares
    
    def on_data(self, data: pd.DataFrame) -> None:
        """
        Process market data and generate signals with dynamic position sizing.
        
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
            
            # Get current symbol
            symbol = self.symbols[0] if self.symbols else "UNKNOWN"
            
            # Store statistics
            self.last_prediction[symbol] = result["probability"]
            self.prediction_history[symbol].append(result["probability"])
            self.confidence_history[symbol].append(confidence)
            
            # Get current price
            current_price = data["close"].iloc[-1]
            
            # Calculate position size based on confidence
            position_size = self.calculate_position_size(symbol, confidence, current_price)
            
            if position_size > 0:
                self.position_sizes_history[symbol].append(position_size)
            
            # Generate signals
            if prediction == 1 and position_size > 0:  # Buy signal
                if not self.has_position(symbol):
                    signal = self.buy(
                        symbol=symbol,
                        quantity=position_size,
                        price=current_price,
                        metadata={
                            "prediction": prediction,
                            "confidence": confidence,
                            "probability": result["probability"],
                            "position_multiplier": position_size * current_price / self.base_position_size
                        }
                    )
                    logger.info(
                        f"{self.name}: BUY {position_size} shares of {symbol} at "
                        f"{current_price:.2f} (confidence={confidence:.3f})"
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
                        f"{self.name}: SELL {symbol} at {current_price:.2f} "
                        f"(confidence={confidence:.3f})"
                    )
            
            else:  # Hold or insufficient confidence
                if confidence < self.min_confidence:
                    logger.debug(
                        f"{self.name}: HOLD {symbol} - insufficient confidence "
                        f"({confidence:.3f} < {self.min_confidence})"
                    )
                else:
                    logger.debug(f"{self.name}: HOLD {symbol}")
        
        except Exception as e:
            logger.error(f"{self.name}: Error processing data: {e}")
    
    def get_confidence_stats(self, symbol: str) -> Dict[str, float]:
        """
        Get confidence statistics for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with confidence statistics
        """
        if symbol not in self.confidence_history:
            return {}
        
        history = self.confidence_history[symbol]
        if len(history) == 0:
            return {}
        
        return {
            "mean_confidence": np.mean(history),
            "std_confidence": np.std(history),
            "min_confidence": np.min(history),
            "max_confidence": np.max(history),
            "last_confidence": history[-1],
            "num_high_confidence": sum(1 for c in history if c > 0.8),
            "num_low_confidence": sum(1 for c in history if c < 0.65)
        }
    
    def get_position_size_stats(self, symbol: str) -> Dict[str, float]:
        """
        Get position size statistics for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with position size statistics
        """
        if symbol not in self.position_sizes_history:
            return {}
        
        history = self.position_sizes_history[symbol]
        if len(history) == 0:
            return {}
        
        return {
            "mean_position_size": np.mean(history),
            "std_position_size": np.std(history),
            "min_position_size": np.min(history),
            "max_position_size": np.max(history),
            "num_positions": len(history)
        }
