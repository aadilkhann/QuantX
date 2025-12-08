"""
Base Model Classes for QuantX ML

This module provides abstract base classes for all ML models.

Key Features:
- Consistent interface across all model types
- Automatic feature scaling
- Model serialization/deserialization
- Runtime configuration
- Device management (CPU/GPU)

All models inherit from these base classes and can be switched at runtime.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import pickle
import joblib
import numpy as np
import pandas as pd
from loguru import logger

from quantx.ml.config import get_ml_config


# ============================================================================
# Model Metadata
# ============================================================================

@dataclass
class ModelMetadata:
    """Metadata for a trained model"""
    name: str
    model_type: str  # "supervised", "timeseries", "reinforcement_learning"
    algorithm: str  # "xgboost", "lstm", "ppo", etc.
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    trained_at: Optional[datetime] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    feature_names: List[str] = field(default_factory=list)
    target_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "model_type": self.model_type,
            "algorithm": self.algorithm,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "feature_names": self.feature_names,
            "target_name": self.target_name
        }


# ============================================================================
# Base Model Class
# ============================================================================

class BaseModel(ABC):
    """
    Abstract base class for all ML models
    
    All models must inherit from this class and implement:
    - fit()
    - predict()
    - save()
    - load()
    
    Features:
    - Consistent interface
    - Automatic device management
    - Model serialization
    - Metadata tracking
    """
    
    def __init__(
        self,
        name: str,
        model_type: str,
        algorithm: str,
        **params
    ):
        """
        Initialize base model
        
        Args:
            name: Model name
            model_type: Type of model (supervised, timeseries, rl)
            algorithm: Algorithm name (xgboost, lstm, etc.)
            **params: Model-specific parameters
        """
        self.name = name
        self.model_type = model_type
        self.algorithm = algorithm
        self.params = params
        
        # Get configuration
        self.config = get_ml_config()
        
        # Model state
        self.model = None
        self.is_fitted = False
        self.feature_names_: Optional[List[str]] = None
        self.target_name_: Optional[str] = None
        
        # Metadata
        self.metadata = ModelMetadata(
            name=name,
            model_type=model_type,
            algorithm=algorithm,
            parameters=params
        )
        
        # Device management
        self.device = self._get_device()
        
        logger.info(f"Initialized {algorithm} model: {name} on {self.device}")
    
    def _get_device(self) -> str:
        """Get compute device based on configuration"""
        return self.config.compute.get_device()
    
    @abstractmethod
    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        **kwargs
    ) -> "BaseModel":
        """
        Train the model
        
        Args:
            X: Features
            y: Target
            **kwargs: Additional training parameters
            
        Returns:
            Self for method chaining
        """
        pass
    
    @abstractmethod
    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features
            **kwargs: Additional prediction parameters
            
        Returns:
            Predictions
        """
        pass
    
    def predict_proba(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """
        Predict class probabilities (for classifiers)
        
        Args:
            X: Features
            **kwargs: Additional parameters
            
        Returns:
            Class probabilities
        """
        raise NotImplementedError(
            f"{self.algorithm} does not support probability predictions"
        )
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Save model to disk
        
        Args:
            path: Path to save model
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update metadata
        self.metadata.trained_at = datetime.now()
        self.metadata.feature_names = self.feature_names_ or []
        self.metadata.target_name = self.target_name_
        
        # Save model and metadata
        model_data = {
            "model": self.model,
            "metadata": self.metadata.to_dict(),
            "feature_names": self.feature_names_,
            "target_name": self.target_name_,
            "is_fitted": self.is_fitted,
            "params": self.params
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Saved model to {path}")
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> "BaseModel":
        """
        Load model from disk
        
        Args:
            path: Path to load model from
            
        Returns:
            Loaded model instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        model_data = joblib.load(path)
        
        # Create instance
        instance = cls(
            name=model_data["metadata"]["name"],
            **model_data["params"]
        )
        
        # Restore state
        instance.model = model_data["model"]
        instance.is_fitted = model_data["is_fitted"]
        instance.feature_names_ = model_data["feature_names"]
        instance.target_name_ = model_data["target_name"]
        
        logger.info(f"Loaded model from {path}")
        return instance
    
    def get_params(self) -> Dict[str, Any]:
        """Get model parameters"""
        return self.params.copy()
    
    def set_params(self, **params) -> "BaseModel":
        """
        Set model parameters
        
        Args:
            **params: Parameters to update
            
        Returns:
            Self for method chaining
        """
        self.params.update(params)
        return self
    
    def get_metadata(self) -> ModelMetadata:
        """Get model metadata"""
        return self.metadata
    
    def _validate_input(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Optional[Union[pd.Series, np.ndarray]] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Validate and convert input data
        
        Args:
            X: Features
            y: Optional target
            
        Returns:
            Tuple of (X, y) as numpy arrays
        """
        # Convert to numpy if needed
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
            X = X.values
        elif isinstance(X, pd.Series):
            X = X.values.reshape(-1, 1)
        
        if y is not None:
            if isinstance(y, pd.Series):
                self.target_name_ = y.name
                y = y.values
            elif isinstance(y, pd.DataFrame):
                self.target_name_ = y.columns[0]
                y = y.values.ravel()
        
        # Validate shapes
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        
        if y is not None and len(y.shape) > 1:
            y = y.ravel()
        
        return X, y
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', algorithm='{self.algorithm}')"


# ============================================================================
# Supervised Learning Model
# ============================================================================

class SupervisedModel(BaseModel):
    """
    Base class for supervised learning models
    
    Supports both classification and regression tasks.
    """
    
    def __init__(
        self,
        name: str,
        algorithm: str,
        task: str = "classification",  # or "regression"
        **params
    ):
        """
        Initialize supervised model
        
        Args:
            name: Model name
            algorithm: Algorithm name
            task: Task type (classification or regression)
            **params: Model parameters
        """
        super().__init__(
            name=name,
            model_type="supervised",
            algorithm=algorithm,
            **params
        )
        self.task = task
        self.classes_ = None
    
    def score(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray]
    ) -> float:
        """
        Calculate model score
        
        Args:
            X: Features
            y: True labels
            
        Returns:
            Score (accuracy for classification, R² for regression)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before scoring")
        
        X, y = self._validate_input(X, y)
        predictions = self.predict(X)
        
        if self.task == "classification":
            # Accuracy
            return np.mean(predictions == y)
        else:
            # R² score
            ss_res = np.sum((y - predictions) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            return 1 - (ss_res / ss_tot)


# ============================================================================
# Time Series Model
# ============================================================================

class TimeSeriesModel(BaseModel):
    """
    Base class for time series models
    
    Handles sequential data with temporal dependencies.
    """
    
    def __init__(
        self,
        name: str,
        algorithm: str,
        sequence_length: int = 60,
        **params
    ):
        """
        Initialize time series model
        
        Args:
            name: Model name
            algorithm: Algorithm name
            sequence_length: Length of input sequences
            **params: Model parameters
        """
        super().__init__(
            name=name,
            model_type="timeseries",
            algorithm=algorithm,
            **params
        )
        self.sequence_length = sequence_length
    
    def create_sequences(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Create sequences from time series data
        
        Args:
            X: Input data
            y: Optional target data
            
        Returns:
            Sequences (and targets if y provided)
        """
        sequences = []
        targets = [] if y is not None else None
        
        for i in range(len(X) - self.sequence_length):
            seq = X[i:i + self.sequence_length]
            sequences.append(seq)
            
            if y is not None:
                targets.append(y[i + self.sequence_length])
        
        sequences = np.array(sequences)
        
        if y is not None:
            targets = np.array(targets)
            return sequences, targets
        
        return sequences


# ============================================================================
# Reinforcement Learning Model
# ============================================================================

class ReinforcementLearningModel(BaseModel):
    """
    Base class for reinforcement learning models
    
    For training trading agents.
    """
    
    def __init__(
        self,
        name: str,
        algorithm: str,
        action_space_size: int,
        state_space_size: int,
        **params
    ):
        """
        Initialize RL model
        
        Args:
            name: Model name
            algorithm: Algorithm name (dqn, ppo, etc.)
            action_space_size: Number of possible actions
            state_space_size: Size of state space
            **params: Model parameters
        """
        super().__init__(
            name=name,
            model_type="reinforcement_learning",
            algorithm=algorithm,
            **params
        )
        self.action_space_size = action_space_size
        self.state_space_size = state_space_size
    
    @abstractmethod
    def select_action(self, state: np.ndarray, **kwargs) -> int:
        """
        Select action given state
        
        Args:
            state: Current state
            **kwargs: Additional parameters
            
        Returns:
            Selected action
        """
        pass
    
    @abstractmethod
    def update(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ) -> Dict[str, float]:
        """
        Update model with experience
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
            
        Returns:
            Dictionary of training metrics
        """
        pass
