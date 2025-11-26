"""
Enhanced Configuration Management for QuantX ML Components

This module extends the base configuration system to support:
1. Runtime configuration changes
2. Multiple configuration sources (files, env vars, runtime)
3. Configuration validation and type safety
4. Environment-specific configurations
5. Dynamic provider/broker switching
"""

from typing import Any, Dict, Optional, List, Union
from pathlib import Path
from enum import Enum
import os
import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

from quantx.core.config import get_config as get_base_config


# ============================================================================
# Enums for Configuration Options
# ============================================================================

class ComputeDevice(str, Enum):
    """Compute device options"""
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Silicon


class MLflowBackend(str, Enum):
    """MLflow tracking backend options"""
    LOCAL = "local"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    REMOTE = "remote"
    DATABRICKS = "databricks"


class DataProvider(str, Enum):
    """Available data providers"""
    YAHOO = "yahoo"
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    BINANCE = "binance"
    CUSTOM = "custom"


class StorageBackend(str, Enum):
    """Data storage backend options"""
    MEMORY = "memory"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    TIMESCALEDB = "timescaledb"
    PARQUET = "parquet"
    HDF5 = "hdf5"


class BrokerType(str, Enum):
    """Available broker types"""
    PAPER = "paper"
    ZERODHA = "zerodha"
    INTERACTIVE_BROKERS = "interactive_brokers"
    BINANCE = "binance"
    ALPACA = "alpaca"


class CloudProvider(str, Enum):
    """Cloud provider options"""
    LOCAL = "local"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DATABRICKS = "databricks"


class ValidationMethod(str, Enum):
    """Model validation methods"""
    HOLDOUT = "holdout"
    KFOLD = "kfold"
    TIMESERIES_CV = "timeseries_cv"
    WALK_FORWARD = "walk_forward"
    PURGED_KFOLD = "purged_kfold"


# ============================================================================
# Configuration Models
# ============================================================================

class ComputeConfig(BaseModel):
    """Compute resource configuration"""
    device: ComputeDevice = ComputeDevice.AUTO
    n_jobs: int = -1
    max_memory_gb: int = 8
    batch_size: int = 32
    mixed_precision: bool = False
    
    def get_device(self) -> str:
        """Get actual device to use based on availability"""
        if self.device == ComputeDevice.AUTO:
            try:
                import torch
                if torch.cuda.is_available():
                    return "cuda"
                elif torch.backends.mps.is_available():
                    return "mps"
            except ImportError:
                pass
            return "cpu"
        return self.device.value


class MLflowConfig(BaseModel):
    """MLflow configuration"""
    tracking_uri: str = "local"
    experiment_name: str = "quantx_trading"
    artifact_location: str = "local"
    registry_uri: Optional[str] = None
    autolog: Dict[str, bool] = {
        "sklearn": True,
        "xgboost": True,
        "lightgbm": True,
        "pytorch": True
    }
    
    def get_tracking_uri(self) -> str:
        """Get MLflow tracking URI"""
        if self.tracking_uri == "local":
            return "file:./mlruns"
        return self.tracking_uri
    
    def get_registry_uri(self) -> str:
        """Get model registry URI"""
        return self.registry_uri or self.get_tracking_uri()


class DataSourceConfig(BaseModel):
    """Data source configuration"""
    primary_provider: DataProvider = DataProvider.YAHOO
    fallback_providers: List[DataProvider] = [DataProvider.ALPHA_VANTAGE]
    storage_backend: StorageBackend = StorageBackend.SQLITE
    providers: Dict[str, Dict[str, Any]] = {}
    storage_config: Dict[str, Dict[str, Any]] = {}


class FeatureEngineeringConfig(BaseModel):
    """Feature engineering configuration"""
    enabled_features: Dict[str, bool] = {
        "technical": True,
        "statistical": True,
        "market_microstructure": False,
        "sentiment": False,
        "fundamental": False
    }
    technical: Dict[str, Any] = {}
    statistical: Dict[str, Any] = {}
    feature_selection: Dict[str, Any] = {
        "enabled": True,
        "method": "mutual_info",
        "max_features": 50
    }


class ModelConfig(BaseModel):
    """Model configuration"""
    available_models: List[str] = [
        "random_forest", "xgboost", "lightgbm", "catboost",
        "lstm", "gru", "transformer", "dqn", "ppo"
    ]
    default_model: str = "xgboost"
    # Model-specific configs stored as dict for flexibility
    model_params: Dict[str, Dict[str, Any]] = {}


class TrainingConfig(BaseModel):
    """Training configuration"""
    target: str = "direction"
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15
    validation_method: ValidationMethod = ValidationMethod.WALK_FORWARD
    n_folds: int = 5
    random_seed: int = 42
    early_stopping: Dict[str, Any] = {
        "enabled": True,
        "patience": 10,
        "min_delta": 0.001
    }
    checkpointing: Dict[str, Any] = {
        "enabled": True,
        "save_best_only": True,
        "monitor": "val_loss",
        "mode": "min"
    }


class BrokerConfig(BaseModel):
    """Broker configuration"""
    active_broker: BrokerType = BrokerType.PAPER
    brokers: Dict[str, Dict[str, Any]] = {}


class DeploymentConfig(BaseModel):
    """Deployment configuration"""
    environment: str = "development"
    cloud_provider: CloudProvider = CloudProvider.LOCAL
    aws: Dict[str, Any] = {}
    gcp: Dict[str, Any] = {}
    azure: Dict[str, Any] = {}


# ============================================================================
# Main ML Configuration
# ============================================================================

class MLConfig(BaseSettings):
    """
    Main ML configuration class with runtime flexibility
    
    This configuration can be:
    1. Loaded from YAML files
    2. Overridden by environment variables
    3. Modified at runtime
    4. Validated for correctness
    """
    
    compute: ComputeConfig = Field(default_factory=ComputeConfig)
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)
    data_sources: DataSourceConfig = Field(default_factory=DataSourceConfig)
    feature_engineering: FeatureEngineeringConfig = Field(default_factory=FeatureEngineeringConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)
    brokers: BrokerConfig = Field(default_factory=BrokerConfig)
    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig)
    
    class Config:
        env_prefix = "QUANTX_ML_"
        env_nested_delimiter = "__"
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> "MLConfig":
        """Load configuration from YAML file"""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(**config_dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MLConfig":
        """Create configuration from dictionary"""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.dict()
    
    def to_yaml(self, output_path: Union[str, Path]) -> None:
        """Save configuration to YAML file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
    
    def update(self, updates: Dict[str, Any]) -> "MLConfig":
        """
        Update configuration with new values at runtime
        
        Example:
            config.update({"compute": {"device": "cuda"}})
        """
        current_dict = self.to_dict()
        self._deep_update(current_dict, updates)
        return self.__class__(**current_dict)
    
    @staticmethod
    def _deep_update(base_dict: Dict, update_dict: Dict) -> None:
        """Recursively update nested dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                MLConfig._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


# ============================================================================
# Configuration Manager - Singleton Pattern
# ============================================================================

class ConfigManager:
    """
    Singleton configuration manager for runtime config changes
    
    Usage:
        # Get manager instance
        manager = ConfigManager.get_instance()
        
        # Load configuration
        manager.load_config("configs/ml_config.yaml")
        
        # Get current config
        config = manager.get_config()
        
        # Update at runtime
        manager.update_config({"compute": {"device": "cuda"}})
        
        # Switch data provider
        manager.switch_data_provider("polygon")
        
        # Switch broker
        manager.switch_broker("zerodha")
    """
    
    _instance: Optional["ConfigManager"] = None
    _config: Optional[MLConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "ConfigManager":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> MLConfig:
        """
        Load configuration from file or use defaults
        
        Args:
            config_path: Path to YAML config file. If None, uses default location.
        
        Returns:
            Loaded ML configuration
        """
        if config_path is None:
            # Try default locations
            default_paths = [
                Path("configs/ml_config.yaml"),
                Path("../configs/ml_config.yaml"),
                Path(__file__).parent.parent.parent / "configs" / "ml_config.yaml"
            ]
            
            for path in default_paths:
                if path.exists():
                    config_path = path
                    break
        
        if config_path and Path(config_path).exists():
            self._config = MLConfig.from_yaml(config_path)
        else:
            # Use defaults
            self._config = MLConfig()
        
        return self._config
    
    def get_config(self) -> MLConfig:
        """Get current configuration"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> MLConfig:
        """Update configuration at runtime"""
        if self._config is None:
            self.load_config()
        
        self._config = self._config.update(updates)
        return self._config
    
    def switch_data_provider(self, provider: Union[str, DataProvider]) -> None:
        """Switch data provider at runtime"""
        if isinstance(provider, str):
            provider = DataProvider(provider)
        
        self.update_config({
            "data_sources": {
                "primary_provider": provider.value
            }
        })
    
    def switch_broker(self, broker: Union[str, BrokerType]) -> None:
        """Switch broker at runtime"""
        if isinstance(broker, str):
            broker = BrokerType(broker)
        
        self.update_config({
            "brokers": {
                "active_broker": broker.value
            }
        })
    
    def switch_compute_device(self, device: Union[str, ComputeDevice]) -> None:
        """Switch compute device at runtime"""
        if isinstance(device, str):
            device = ComputeDevice(device)
        
        self.update_config({
            "compute": {
                "device": device.value
            }
        })
    
    def switch_mlflow_backend(self, backend: str) -> None:
        """Switch MLflow tracking backend at runtime"""
        self.update_config({
            "mlflow": {
                "tracking_uri": backend
            }
        })
    
    def enable_cloud_provider(self, provider: Union[str, CloudProvider], config: Dict[str, Any]) -> None:
        """Enable and configure cloud provider"""
        if isinstance(provider, str):
            provider = CloudProvider(provider)
        
        self.update_config({
            "deployment": {
                "cloud_provider": provider.value,
                provider.value: config
            }
        })


# ============================================================================
# Convenience Functions
# ============================================================================

def get_ml_config() -> MLConfig:
    """Get current ML configuration"""
    return ConfigManager.get_instance().get_config()


def load_ml_config(config_path: Optional[Union[str, Path]] = None) -> MLConfig:
    """Load ML configuration from file"""
    return ConfigManager.get_instance().load_config(config_path)


def update_ml_config(updates: Dict[str, Any]) -> MLConfig:
    """Update ML configuration at runtime"""
    return ConfigManager.get_instance().update_config(updates)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Load configuration
    config = load_ml_config("configs/ml_config.yaml")
    
    print(f"Current device: {config.compute.get_device()}")
    print(f"Current data provider: {config.data_sources.primary_provider}")
    print(f"Current broker: {config.brokers.active_broker}")
    
    # Runtime updates
    manager = ConfigManager.get_instance()
    
    # Switch to GPU if available
    manager.switch_compute_device("cuda")
    
    # Switch to different data provider
    manager.switch_data_provider("polygon")
    
    # Switch broker
    manager.switch_broker("zerodha")
    
    # Enable AWS cloud
    manager.enable_cloud_provider("aws", {
        "region": "us-east-1",
        "s3_bucket": "my-quantx-bucket"
    })
    
    # Get updated config
    updated_config = manager.get_config()
    print(f"\nUpdated device: {updated_config.compute.get_device()}")
    print(f"Updated provider: {updated_config.data_sources.primary_provider}")
    print(f"Updated broker: {updated_config.brokers.active_broker}")
