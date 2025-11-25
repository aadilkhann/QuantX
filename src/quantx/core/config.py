"""
Configuration Management for QuantX

Provides centralized configuration loading from environment variables and files.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class AppConfig(BaseSettings):
    """Application configuration"""

    env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    url: str = Field(default="postgresql://quantx:password@localhost:5432/quantx", alias="DATABASE_URL")
    pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class RedisConfig(BaseSettings):
    """Redis configuration"""

    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class APIConfig(BaseSettings):
    """API server configuration"""

    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    workers: int = Field(default=4, alias="API_WORKERS")
    reload: bool = Field(default=False, alias="API_RELOAD")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins"""
        return [origin.strip() for origin in v.split(",") if origin.strip()]


class LoggingConfig(BaseSettings):
    """Logging configuration"""

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    format: str = Field(default="json", alias="LOG_FORMAT")
    file: Optional[str] = Field(default=None, alias="LOG_FILE")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class DataProviderConfig(BaseSettings):
    """Data provider configuration"""

    yahoo_enabled: bool = Field(default=True, alias="YAHOO_FINANCE_ENABLED")
    alpha_vantage_key: Optional[str] = Field(default=None, alias="ALPHA_VANTAGE_API_KEY")
    alpha_vantage_enabled: bool = Field(default=False, alias="ALPHA_VANTAGE_ENABLED")
    polygon_key: Optional[str] = Field(default=None, alias="POLYGON_API_KEY")
    polygon_enabled: bool = Field(default=False, alias="POLYGON_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BacktestConfig(BaseSettings):
    """Backtesting configuration"""

    max_concurrent: int = Field(default=10, alias="BACKTEST_MAX_CONCURRENT")
    timeout: int = Field(default=3600, alias="BACKTEST_TIMEOUT")
    cache_enabled: bool = Field(default=True, alias="BACKTEST_CACHE_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class RiskConfig(BaseSettings):
    """Risk management configuration"""

    max_position_size: float = Field(default=0.1, alias="RISK_MAX_POSITION_SIZE")
    max_daily_loss: float = Field(default=0.02, alias="RISK_MAX_DAILY_LOSS")
    max_drawdown: float = Field(default=0.15, alias="RISK_MAX_DRAWDOWN")
    max_leverage: float = Field(default=1.0, alias="RISK_MAX_LEVERAGE")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("max_position_size", "max_daily_loss", "max_drawdown")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate percentage values are between 0 and 1"""
        if not 0 < v <= 1:
            raise ValueError(f"Value must be between 0 and 1, got {v}")
        return v


class MLConfig(BaseSettings):
    """Machine learning configuration"""

    model_path: str = Field(default="./data/models", alias="ML_MODEL_PATH")
    cache_enabled: bool = Field(default=True, alias="ML_CACHE_ENABLED")
    gpu_enabled: bool = Field(default=False, alias="ML_GPU_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Config:
    """
    Main configuration class

    Aggregates all configuration sections and provides easy access.
    """

    def __init__(self, env_file: Optional[str] = None) -> None:
        """
        Initialize configuration

        Args:
            env_file: Path to .env file (defaults to .env in current directory)
        """
        if env_file:
            os.environ["ENV_FILE"] = env_file

        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()
        self.data_providers = DataProviderConfig()
        self.backtest = BacktestConfig()
        self.risk = RiskConfig()
        self.ml = MLConfig()

        logger.info("Configuration loaded for environment: {}", self.app.env)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "app": self.app.model_dump(),
            "database": self.database.model_dump(),
            "redis": self.redis.model_dump(),
            "api": self.api.model_dump(),
            "logging": self.logging.model_dump(),
            "data_providers": self.data_providers.model_dump(),
            "backtest": self.backtest.model_dump(),
            "risk": self.risk.model_dump(),
            "ml": self.ml.model_dump(),
        }

    @classmethod
    def from_env(cls, env_file: str = ".env") -> "Config":
        """
        Create configuration from environment file

        Args:
            env_file: Path to environment file

        Returns:
            Config instance
        """
        return cls(env_file=env_file)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config(env_file: Optional[str] = None) -> Config:
    """
    Reload configuration

    Args:
        env_file: Path to environment file

    Returns:
        New Config instance
    """
    global _config
    _config = Config(env_file=env_file)
    return _config
