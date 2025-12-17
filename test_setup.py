#!/usr/bin/env python3
"""
QuantX Setup Validation Script
Run this to verify your installation is working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_python_version() -> bool:
    """Test Python version."""
    print_section("1. Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("✅ Python version is compatible (3.11+)")
        return True
    else:
        print("❌ Python 3.11 or higher is required")
        return False


def test_core_imports() -> bool:
    """Test core module imports."""
    print_section("2. Core Module Imports")
    
    tests = [
        ("quantx.core.config", "Config"),
        ("quantx.core.events", "EventBus"),
        ("quantx.data.providers.yahoo", "YahooFinanceProvider"),
        ("quantx.strategies", "StrategyRegistry"),
        ("quantx.backtesting", "BacktestEngine"),
    ]
    
    all_passed = True
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"❌ {module_name}.{class_name} - {e}")
            all_passed = False
    
    return all_passed


def test_phase2_imports() -> bool:
    """Test Phase 2 (ML) imports."""
    print_section("3. Phase 2 (ML) Module Imports")
    
    tests = [
        ("quantx.ml.features", "features module"),
        ("quantx.ml.models.traditional", "traditional ML models"),
        ("quantx.ml.evaluation", "evaluation module"),
    ]
    
    passed_count = 0
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✅ {description}")
            passed_count += 1
        except (ImportError, NameError) as e:
            print(f"⚠️  {description} - Import failed (optional)")
            # ML modules are optional, so don't fail the test
    
    # Phase 2 is optional - pass if at least one module loads
    return passed_count >= 1


def test_phase3_imports() -> bool:
    """Test Phase 3 (Live Trading) imports."""
    print_section("4. Phase 3 (Live Trading) Module Imports")
    
    tests = [
        ("quantx.execution.brokers", "PaperBroker"),
        ("quantx.execution.orders", "OrderManager"),
        ("quantx.execution.risk", "RiskManager"),
    ]
    
    all_passed = True
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"❌ {module_name}.{class_name} - {e}")
            all_passed = False
    
    return all_passed


def test_dependencies() -> bool:
    """Test critical dependencies."""
    print_section("5. Critical Dependencies")
    
    dependencies = [
        "pandas",
        "numpy",
        "yfinance",
        "pydantic",
        "loguru",
    ]
    
    all_passed = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Not installed")
            all_passed = False
    
    return all_passed


def test_optional_dependencies() -> bool:
    """Test optional ML dependencies."""
    print_section("6. Optional ML Dependencies")
    
    dependencies = [
        ("scikit-learn", "sklearn"),
        ("xgboost", "xgboost"),
        ("lightgbm", "lightgbm"),
        ("PyTorch", "torch"),
        ("MLflow", "mlflow"),
    ]
    
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} - Not installed (optional)")
    
    return True  # These are optional


def test_data_fetch() -> bool:
    """Test data fetching capability."""
    print_section("7. Data Fetching Test")
    
    try:
        from datetime import datetime, timedelta
        from quantx.data.providers.yahoo import YahooFinanceProvider
        
        print("Creating Yahoo Finance provider...")
        provider = YahooFinanceProvider()
        
        print("Fetching test data for AAPL (last 7 days)...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        data = provider.get_historical_data("AAPL", start_date, end_date)
        
        if data is not None and len(data) > 0:
            print(f"✅ Successfully fetched {len(data)} rows of data")
            print(f"   Columns: {', '.join(data.columns.tolist())}")
            return True
        else:
            print("❌ No data fetched")
            return False
            
    except Exception as e:
        print(f"❌ Data fetch failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          QuantX Setup Validation Script                  ║
    ║          Testing your installation...                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    results = {
        "Python Version": test_python_version(),
        "Core Imports": test_core_imports(),
        "Phase 2 (ML) Imports": test_phase2_imports(),
        "Phase 3 (Live) Imports": test_phase3_imports(),
        "Critical Dependencies": test_dependencies(),
        "Optional Dependencies": test_optional_dependencies(),
        "Data Fetching": test_data_fetch(),
    }
    
    # Summary
    print_section("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your QuantX installation is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python examples/fetch_data.py")
        print("  2. Run: python examples/complete_backtest.py")
        print("  3. Read: SETUP_AND_RUN_GUIDE.md for more examples")
        return 0
    elif passed >= 5:
        print("\n⚠️  Most tests passed. You can proceed with basic functionality.")
        print("   Optional components may not work until dependencies are installed.")
        return 0
    else:
        print("\n❌ Multiple tests failed. Please check:")
        print("  1. Virtual environment is activated")
        print("  2. Dependencies installed: pip install -r requirements.txt")
        print("  3. You're in the QuantX directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())
