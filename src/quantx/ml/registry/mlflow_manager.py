"""
MLflow Integration for Model Management.

This module provides MLflow integration for experiment tracking,
model registry, and model versioning.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import pandas as pd
from loguru import logger

try:
    import mlflow
    import mlflow.sklearn
    import mlflow.xgboost
    import mlflow.lightgbm
    import mlflow.pytorch
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available. Install with: pip install mlflow")


class MLflowManager:
    """
    Manager for MLflow experiment tracking and model registry.
    
    Example:
        >>> manager = MLflowManager(
        ...     tracking_uri="file:///path/to/mlruns",
        ...     experiment_name="trading_models"
        ... )
        >>> 
        >>> # Track training run
        >>> with manager.start_run(run_name="xgb_v1"):
        ...     manager.log_params({"n_estimators": 100})
        ...     manager.log_metrics({"accuracy": 0.85})
        ...     manager.log_model(model, "xgb_model")
        >>> 
        >>> # Register model
        >>> manager.register_model("xgb_model", "XGBoost Classifier")
    """
    
    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: str = "quantx_trading",
        registry_uri: Optional[str] = None,
        auto_log: bool = True
    ):
        """
        Initialize MLflow manager.
        
        Args:
            tracking_uri: MLflow tracking server URI
            experiment_name: Name of the experiment
            registry_uri: Model registry URI (defaults to tracking_uri)
            auto_log: Enable automatic logging
        """
        if not MLFLOW_AVAILABLE:
            raise ImportError("MLflow is required. Install with: pip install mlflow")
        
        self.tracking_uri = tracking_uri or "file:///tmp/mlruns"
        self.experiment_name = experiment_name
        self.registry_uri = registry_uri or tracking_uri
        self.auto_log = auto_log
        
        # Set URIs
        mlflow.set_tracking_uri(self.tracking_uri)
        if self.registry_uri:
            mlflow.set_registry_uri(self.registry_uri)
        
        # Create or get experiment
        self.experiment = mlflow.get_experiment_by_name(experiment_name)
        if self.experiment is None:
            self.experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"Created MLflow experiment: {experiment_name}")
        else:
            self.experiment_id = self.experiment.experiment_id
            logger.info(f"Using existing MLflow experiment: {experiment_name}")
        
        # Enable autologging if requested
        if self.auto_log:
            mlflow.sklearn.autolog()
            mlflow.xgboost.autolog()
            mlflow.lightgbm.autolog()
            mlflow.pytorch.autolog()
            logger.info("Enabled MLflow autologging")
    
    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Start a new MLflow run.
        
        Args:
            run_name: Name for the run
            tags: Tags to attach to the run
            
        Returns:
            MLflow run context manager
        """
        return mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=run_name,
            tags=tags
        )
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log parameters to current run.
        
        Args:
            params: Dictionary of parameters
        """
        mlflow.log_params(params)
        logger.debug(f"Logged {len(params)} parameters")
    
    def log_param(self, key: str, value: Any) -> None:
        """
        Log a single parameter.
        
        Args:
            key: Parameter name
            value: Parameter value
        """
        mlflow.log_param(key, value)
    
    def log_metrics(
        self,
        metrics: Dict[str, float],
        step: Optional[int] = None
    ) -> None:
        """
        Log metrics to current run.
        
        Args:
            metrics: Dictionary of metrics
            step: Optional step number
        """
        mlflow.log_metrics(metrics, step=step)
        logger.debug(f"Logged {len(metrics)} metrics")
    
    def log_metric(
        self,
        key: str,
        value: float,
        step: Optional[int] = None
    ) -> None:
        """
        Log a single metric.
        
        Args:
            key: Metric name
            value: Metric value
            step: Optional step number
        """
        mlflow.log_metric(key, value, step=step)
    
    def log_model(
        self,
        model: Any,
        artifact_path: str,
        registered_model_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Log a model to MLflow.
        
        Args:
            model: Model to log
            artifact_path: Path within run artifacts
            registered_model_name: Name for model registry
            **kwargs: Additional arguments for model logging
        """
        # Determine model type and log appropriately
        model_type = type(model).__name__
        
        if "XGBoost" in model_type or "xgb" in str(type(model).__module__):
            mlflow.xgboost.log_model(
                model,
                artifact_path,
                registered_model_name=registered_model_name,
                **kwargs
            )
        elif "LightGBM" in model_type or "lgb" in str(type(model).__module__):
            mlflow.lightgbm.log_model(
                model,
                artifact_path,
                registered_model_name=registered_model_name,
                **kwargs
            )
        elif "torch" in str(type(model).__module__) or "pytorch" in str(type(model).__module__):
            mlflow.pytorch.log_model(
                model,
                artifact_path,
                registered_model_name=registered_model_name,
                **kwargs
            )
        else:
            # Default to sklearn
            mlflow.sklearn.log_model(
                model,
                artifact_path,
                registered_model_name=registered_model_name,
                **kwargs
            )
        
        logger.info(f"Logged model to {artifact_path}")
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """
        Log an artifact file.
        
        Args:
            local_path: Path to local file
            artifact_path: Path within run artifacts
        """
        mlflow.log_artifact(local_path, artifact_path)
        logger.debug(f"Logged artifact: {local_path}")
    
    def log_dict(self, dictionary: Dict, artifact_file: str) -> None:
        """
        Log a dictionary as JSON artifact.
        
        Args:
            dictionary: Dictionary to log
            artifact_file: Filename for artifact
        """
        mlflow.log_dict(dictionary, artifact_file)
        logger.debug(f"Logged dictionary to {artifact_file}")
    
    def log_figure(self, figure, artifact_file: str) -> None:
        """
        Log a matplotlib figure.
        
        Args:
            figure: Matplotlib figure
            artifact_file: Filename for artifact
        """
        mlflow.log_figure(figure, artifact_file)
        logger.debug(f"Logged figure to {artifact_file}")
    
    def log_dataframe(self, df: pd.DataFrame, artifact_file: str) -> None:
        """
        Log a pandas DataFrame.
        
        Args:
            df: DataFrame to log
            artifact_file: Filename for artifact
        """
        # Save to temp file and log
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            mlflow.log_artifact(f.name, artifact_file)
        logger.debug(f"Logged dataframe to {artifact_file}")
    
    def register_model(
        self,
        model_uri: str,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None
    ):
        """
        Register a model in the model registry.
        
        Args:
            model_uri: URI of the model (e.g., "runs:/<run_id>/model")
            name: Name for the registered model
            tags: Tags for the model version
            description: Description of the model
            
        Returns:
            ModelVersion object
        """
        model_version = mlflow.register_model(model_uri, name)
        
        # Add tags if provided
        if tags:
            client = mlflow.tracking.MlflowClient()
            for key, value in tags.items():
                client.set_model_version_tag(name, model_version.version, key, value)
        
        # Add description if provided
        if description:
            client = mlflow.tracking.MlflowClient()
            client.update_model_version(
                name,
                model_version.version,
                description=description
            )
        
        logger.info(f"Registered model '{name}' version {model_version.version}")
        return model_version
    
    def load_model(self, model_uri: str) -> Any:
        """
        Load a model from MLflow.
        
        Args:
            model_uri: URI of the model
            
        Returns:
            Loaded model
        """
        model = mlflow.pyfunc.load_model(model_uri)
        logger.info(f"Loaded model from {model_uri}")
        return model
    
    def transition_model_stage(
        self,
        name: str,
        version: int,
        stage: str
    ) -> None:
        """
        Transition a model version to a new stage.
        
        Args:
            name: Registered model name
            version: Model version number
            stage: Target stage (Staging, Production, Archived)
        """
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=name,
            version=version,
            stage=stage
        )
        logger.info(f"Transitioned {name} v{version} to {stage}")
    
    def get_latest_model_version(
        self,
        name: str,
        stage: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get the latest version of a registered model.
        
        Args:
            name: Registered model name
            stage: Optional stage filter (Production, Staging, etc.)
            
        Returns:
            Latest model version or None
        """
        client = mlflow.tracking.MlflowClient()
        
        if stage:
            versions = client.get_latest_versions(name, stages=[stage])
        else:
            versions = client.search_model_versions(f"name='{name}'")
        
        if versions:
            latest = max(versions, key=lambda v: int(v.version))
            logger.info(f"Found {name} version {latest.version}")
            return latest
        
        logger.warning(f"No versions found for model '{name}'")
        return None
    
    def list_experiments(self) -> List[Any]:
        """List all experiments."""
        client = mlflow.tracking.MlflowClient()
        return client.search_experiments()
    
    def list_registered_models(self) -> List[Any]:
        """List all registered models."""
        client = mlflow.tracking.MlflowClient()
        return client.search_registered_models()
    
    def delete_experiment(self, experiment_id: str) -> None:
        """Delete an experiment."""
        mlflow.delete_experiment(experiment_id)
        logger.info(f"Deleted experiment {experiment_id}")
    
    def delete_run(self, run_id: str) -> None:
        """Delete a run."""
        mlflow.delete_run(run_id)
        logger.info(f"Deleted run {run_id}")


class ExperimentTracker:
    """
    Simplified interface for tracking experiments.
    
    Example:
        >>> tracker = ExperimentTracker("trading_models")
        >>> tracker.track_training(
        ...     model=model,
        ...     params={"n_estimators": 100},
        ...     metrics={"accuracy": 0.85},
        ...     run_name="xgb_v1"
        ... )
    """
    
    def __init__(
        self,
        experiment_name: str = "quantx_trading",
        tracking_uri: Optional[str] = None
    ):
        """
        Initialize experiment tracker.
        
        Args:
            experiment_name: Name of the experiment
            tracking_uri: MLflow tracking server URI
        """
        self.manager = MLflowManager(
            tracking_uri=tracking_uri,
            experiment_name=experiment_name
        )
    
    def track_training(
        self,
        model: Any,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        artifacts: Optional[Dict[str, str]] = None,
        register_model: bool = False,
        model_name: Optional[str] = None
    ) -> str:
        """
        Track a complete training run.
        
        Args:
            model: Trained model
            params: Model parameters
            metrics: Evaluation metrics
            run_name: Name for the run
            tags: Tags for the run
            artifacts: Additional artifacts to log {path: artifact_path}
            register_model: Whether to register the model
            model_name: Name for registered model
            
        Returns:
            Run ID
        """
        with self.manager.start_run(run_name=run_name, tags=tags) as run:
            # Log parameters
            self.manager.log_params(params)
            
            # Log metrics
            self.manager.log_metrics(metrics)
            
            # Log model
            self.manager.log_model(model, "model")
            
            # Log additional artifacts
            if artifacts:
                for local_path, artifact_path in artifacts.items():
                    self.manager.log_artifact(local_path, artifact_path)
            
            # Register model if requested
            if register_model and model_name:
                model_uri = f"runs:/{run.info.run_id}/model"
                self.manager.register_model(model_uri, model_name)
            
            logger.info(f"Tracked training run: {run.info.run_id}")
            return run.info.run_id


class ModelRegistry:
    """
    Simplified interface for model registry operations.
    
    Example:
        >>> registry = ModelRegistry()
        >>> registry.register("runs:/abc123/model", "XGBoost Classifier")
        >>> model = registry.load_production_model("XGBoost Classifier")
    """
    
    def __init__(self, tracking_uri: Optional[str] = None):
        """
        Initialize model registry.
        
        Args:
            tracking_uri: MLflow tracking server URI
        """
        self.manager = MLflowManager(tracking_uri=tracking_uri)
    
    def register(
        self,
        model_uri: str,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """Register a model."""
        return self.manager.register_model(
            model_uri,
            name,
            tags=tags,
            description=description
        )
    
    def load_production_model(self, name: str) -> Any:
        """Load the production version of a model."""
        version = self.manager.get_latest_model_version(name, stage="Production")
        if version:
            model_uri = f"models:/{name}/{version.version}"
            return self.manager.load_model(model_uri)
        raise ValueError(f"No production model found for '{name}'")
    
    def load_latest_model(self, name: str) -> Any:
        """Load the latest version of a model."""
        version = self.manager.get_latest_model_version(name)
        if version:
            model_uri = f"models:/{name}/{version.version}"
            return self.manager.load_model(model_uri)
        raise ValueError(f"No model found for '{name}'")
    
    def promote_to_production(self, name: str, version: int) -> None:
        """Promote a model version to production."""
        self.manager.transition_model_stage(name, version, "Production")
    
    def archive_model(self, name: str, version: int) -> None:
        """Archive a model version."""
        self.manager.transition_model_stage(name, version, "Archived")
