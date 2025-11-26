"""
Example: Runtime Configuration Flexibility

This example demonstrates how to:
1. Start with minimal resources (CPU, free data, local storage)
2. Switch configurations at runtime
3. Upgrade to cloud/GPU when ready
4. Change data providers and brokers on the fly

NO CODE CHANGES REQUIRED - just configuration!
"""

from quantx.ml import (
    ConfigManager,
    get_ml_config,
    update_ml_config,
    ComputeDevice,
    DataProvider,
    BrokerType,
    CloudProvider
)


def scenario_1_local_development():
    """
    Scenario 1: Local Development (No Budget)
    
    - CPU training
    - Free Yahoo Finance data
    - Paper trading
    - Local MLflow
    - SQLite storage
    """
    print("=" * 70)
    print("SCENARIO 1: Local Development (No Budget Required)")
    print("=" * 70)
    
    # Load default configuration
    config = get_ml_config()
    
    print(f"\n✓ Compute Device: {config.compute.get_device()}")
    print(f"✓ Data Provider: {config.data_sources.primary_provider}")
    print(f"✓ Broker: {config.brokers.active_broker}")
    print(f"✓ MLflow: {config.mlflow.get_tracking_uri()}")
    print(f"✓ Storage: {config.data_sources.storage_backend}")
    
    print("\n💡 This setup costs $0 and works on any laptop!")
    print("   You can train models, backtest strategies, and develop locally.")


def scenario_2_got_gpu():
    """
    Scenario 2: Got a GPU (or rented cloud GPU)
    
    Just change device config - everything else stays the same!
    """
    print("\n" + "=" * 70)
    print("SCENARIO 2: Upgraded to GPU")
    print("=" * 70)
    
    manager = ConfigManager.get_instance()
    
    # Switch to GPU with ONE line
    manager.switch_compute_device("cuda")
    
    config = manager.get_config()
    print(f"\n✓ Compute Device: {config.compute.get_device()} (UPGRADED!)")
    print(f"✓ Data Provider: {config.data_sources.primary_provider} (unchanged)")
    print(f"✓ Broker: {config.brokers.active_broker} (unchanged)")
    
    print("\n💡 Now training is 10-100x faster!")
    print("   Same code, same data, just faster execution.")


def scenario_3_premium_data():
    """
    Scenario 3: Got funding - upgrade to premium data
    
    Switch from Yahoo Finance to Polygon.io
    """
    print("\n" + "=" * 70)
    print("SCENARIO 3: Premium Data Source")
    print("=" * 70)
    
    manager = ConfigManager.get_instance()
    
    # Switch to premium data provider
    manager.switch_data_provider("polygon")
    
    # Update provider config with API key
    manager.update_config({
        "data_sources": {
            "providers": {
                "polygon": {
                    "enabled": True,
                    "api_key": "your-polygon-api-key",
                    "tier": "developer"  # or "advanced"
                }
            }
        }
    })
    
    config = manager.get_config()
    print(f"\n✓ Compute Device: {config.compute.get_device()}")
    print(f"✓ Data Provider: {config.data_sources.primary_provider} (UPGRADED!)")
    print(f"✓ Fallback: {config.data_sources.fallback_providers}")
    
    print("\n💡 Now you have:")
    print("   - Real-time data")
    print("   - More symbols")
    print("   - Better data quality")
    print("   - Automatic fallback to Yahoo if Polygon fails")


def scenario_4_live_trading():
    """
    Scenario 4: Ready for live trading
    
    Switch from paper trading to real broker
    """
    print("\n" + "=" * 70)
    print("SCENARIO 4: Live Trading with Real Broker")
    print("=" * 70)
    
    manager = ConfigManager.get_instance()
    
    # Switch to Zerodha (or any other broker)
    manager.switch_broker("zerodha")
    
    # Configure broker credentials
    manager.update_config({
        "brokers": {
            "zerodha": {
                "enabled": True,
                "api_key": "your-zerodha-api-key",
                "api_secret": "your-zerodha-secret",
                # ... other credentials
            }
        }
    })
    
    config = manager.get_config()
    print(f"\n✓ Compute Device: {config.compute.get_device()}")
    print(f"✓ Data Provider: {config.data_sources.primary_provider}")
    print(f"✓ Broker: {config.brokers.active_broker} (LIVE!)")
    
    print("\n⚠️  WARNING: Now trading with real money!")
    print("   Make sure you've thoroughly backtested your strategy.")


def scenario_5_cloud_deployment():
    """
    Scenario 5: Deploy to AWS with managed services
    
    Use AWS SageMaker for training, S3 for storage, managed MLflow
    """
    print("\n" + "=" * 70)
    print("SCENARIO 5: Cloud Deployment (AWS)")
    print("=" * 70)
    
    manager = ConfigManager.get_instance()
    
    # Enable AWS cloud provider
    manager.enable_cloud_provider("aws", {
        "region": "us-east-1",
        "s3_bucket": "my-quantx-bucket",
        "ec2_instance_type": "p3.2xlarge",  # GPU instance
        "sagemaker_enabled": True
    })
    
    # Switch to cloud MLflow
    manager.switch_mlflow_backend("http://mlflow-server.example.com:5000")
    
    # Update storage to use S3
    manager.update_config({
        "data_sources": {
            "storage_backend": "parquet",
            "storage_config": {
                "parquet": {
                    "path": "s3://my-quantx-bucket/data/"
                }
            }
        }
    })
    
    config = manager.get_config()
    print(f"\n✓ Cloud Provider: {config.deployment.cloud_provider}")
    print(f"✓ Compute Device: cuda (AWS GPU)")
    print(f"✓ MLflow: Remote server")
    print(f"✓ Storage: S3")
    
    print("\n💡 Now you have:")
    print("   - Scalable GPU training")
    print("   - Managed MLflow")
    print("   - Distributed storage")
    print("   - High availability")


def scenario_6_multi_strategy_portfolio():
    """
    Scenario 6: Running multiple strategies with different configs
    
    Each strategy can have its own configuration!
    """
    print("\n" + "=" * 70)
    print("SCENARIO 6: Multi-Strategy Portfolio")
    print("=" * 70)
    
    # Strategy 1: ML-based on GPU
    config_ml = get_ml_config()
    config_ml = config_ml.update({
        "compute": {"device": "cuda"},
        "models": {"default_model": "lstm"}
    })
    
    # Strategy 2: Traditional ML on CPU
    config_traditional = get_ml_config()
    config_traditional = config_traditional.update({
        "compute": {"device": "cpu"},
        "models": {"default_model": "xgboost"}
    })
    
    # Strategy 3: RL agent
    config_rl = get_ml_config()
    config_rl = config_rl.update({
        "compute": {"device": "cuda"},
        "models": {"default_model": "ppo"}
    })
    
    print("\n✓ Strategy 1 (LSTM): GPU, Deep Learning")
    print("✓ Strategy 2 (XGBoost): CPU, Traditional ML")
    print("✓ Strategy 3 (PPO): GPU, Reinforcement Learning")
    
    print("\n💡 Each strategy runs independently with optimal config!")


def scenario_7_ab_testing():
    """
    Scenario 7: A/B Testing different configurations
    
    Test which setup performs better
    """
    print("\n" + "=" * 70)
    print("SCENARIO 7: A/B Testing Configurations")
    print("=" * 70)
    
    # Configuration A: Conservative
    config_a = get_ml_config()
    config_a = config_a.update({
        "feature_engineering": {
            "enabled_features": {
                "technical": True,
                "statistical": True,
                "sentiment": False
            }
        },
        "models": {"default_model": "random_forest"}
    })
    
    # Configuration B: Aggressive
    config_b = get_ml_config()
    config_b = config_b.update({
        "feature_engineering": {
            "enabled_features": {
                "technical": True,
                "statistical": True,
                "sentiment": True,
                "fundamental": True
            }
        },
        "models": {"default_model": "transformer"}
    })
    
    print("\n✓ Config A: Simple features, Random Forest")
    print("✓ Config B: All features, Transformer")
    
    print("\n💡 Run both in parallel and compare results!")


def scenario_8_disaster_recovery():
    """
    Scenario 8: Disaster Recovery / Failover
    
    Automatic fallback when primary services fail
    """
    print("\n" + "=" * 70)
    print("SCENARIO 8: Disaster Recovery")
    print("=" * 70)
    
    config = get_ml_config()
    
    print("\n✓ Primary Data Provider: polygon")
    print("✓ Fallback Providers: [alpha_vantage, yahoo]")
    print("\n💡 If Polygon fails:")
    print("   1. Automatically try Alpha Vantage")
    print("   2. If that fails, fall back to Yahoo Finance")
    print("   3. System keeps running!")
    
    print("\n✓ Primary Broker: zerodha")
    print("✓ Backup: paper trading")
    print("\n💡 If broker connection fails:")
    print("   1. Automatically switch to paper trading")
    print("   2. Alert sent to admin")
    print("   3. No trades lost!")


def main():
    """Run all scenarios"""
    
    print("\n")
    print("🚀 " * 35)
    print("QuantX Phase 2: Runtime Configuration Flexibility Demo")
    print("🚀 " * 35)
    
    # Run all scenarios
    scenario_1_local_development()
    scenario_2_got_gpu()
    scenario_3_premium_data()
    scenario_4_live_trading()
    scenario_5_cloud_deployment()
    scenario_6_multi_strategy_portfolio()
    scenario_7_ab_testing()
    scenario_8_disaster_recovery()
    
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("""
1. ✅ Start with $0 budget (CPU, free data, local)
2. ✅ Upgrade incrementally as you get funding
3. ✅ NO CODE CHANGES - just configuration
4. ✅ Switch providers/brokers at runtime
5. ✅ Run multiple configs simultaneously
6. ✅ Automatic failover and disaster recovery
7. ✅ A/B test different setups
8. ✅ Deploy anywhere (local, AWS, GCP, Azure)

🎯 This is the power of flexible architecture!
    """)


if __name__ == "__main__":
    main()
