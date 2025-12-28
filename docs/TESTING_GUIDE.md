# QuantX Testing Guide

**Quick Start Guide for Running Tests**

---

## 🚀 Quick Start

### Run All Tests
```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v
```

### Run Tests with Coverage
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v --cov=src/quantx --cov-report=html --cov-report=term-missing
```

### View Coverage Report
```bash
# After running tests with coverage
open htmlcov/index.html  # Opens in browser
```

---

## 📋 Test Commands

### Basic Commands

**Run all tests (verbose)**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v
```

**Run specific test file**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/unit/execution/test_live_engine.py -v
```

**Run specific test class**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/unit/execution/test_live_engine.py::TestLiveExecutionEngineLifecycle -v
```

**Run specific test**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/unit/execution/test_live_engine.py::TestLiveExecutionEngineLifecycle::test_engine_initialization -v
```

### Coverage Commands

**Full coverage report**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ --cov=src/quantx --cov-report=html --cov-report=term-missing
```

**Coverage for specific module**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ --cov=src/quantx/execution --cov-report=term-missing
```

**Check coverage threshold**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ --cov=src/quantx --cov-fail-under=70
```

### Output Format Options

**Minimal output**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -q
```

**Show test durations**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v --durations=10
```

**Stop on first failure**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v -x
```

**Show local variables on failure**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v -l
```

**Show print statements**:
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v -s
```

---

## 📊 Understanding Test Output

### Sample Output

```
============================= test session starts ==============================
platform darwin -- Python 3.11.5
cachedir: .pytest_cache
rootdir: /Users/adii/Builds/Algo-Trading/QuantX
plugins: cov-4.1.0, asyncio-0.21.1
collected 17 items

tests/unit/execution/test_live_engine.py::TestLiveExecutionEngineLifecycle::test_engine_initialization PASSED [  5%]
tests/unit/execution/test_live_engine.py::TestLiveExecutionEngineLifecycle::test_engine_start PASSED [ 11%]
tests/unit/execution/test_live_engine.py::TestLiveExecutionEngineLifecycle::test_engine_stop FAILED [ 17%]
...

============================== 17 passed, 0 failed in 2.34s =============================
```

### Status Indicators
- ✅ **PASSED** - Test succeeded
- ❌ **FAILED** - Test failed (assertion error)
- ⚠️ **ERROR** - Test error (exception during setup/execution)
- ⏭️ **SKIPPED** - Test was skipped
- **xfail** - Expected to fail (marked with @pytest.mark.xfail)

### Coverage Output

```
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
src/quantx/execution/live_engine.py      235    182    23%   83-109, 113-120, ...
src/quantx/execution/position_sync.py    114     75    34%   51, 55, 93-102, ...
--------------------------------------------------------------------
TOTAL                                   4625   3845    17%
```

**Columns**:
- **Stmts**: Total statements
- **Miss**: Statements not covered
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

---

## 🎯 Common Testing Scenarios

### 1. Quick Health Check
```bash
# Run all tests, stop on first failure
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v -x
```

### 2. Full Test Run with Coverage
```bash
# Complete test run with HTML coverage report
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v \
  --cov=src/quantx \
  --cov-report=html \
  --cov-report=term-missing \
  --durations=5

# Open coverage report
open htmlcov/index.html
```

### 3. Debug Failing Test
```bash
# Run specific test with full output
PYTHONPATH="$(pwd)/src" python3 -m pytest \
  tests/unit/execution/test_live_engine.py::TestLiveExecutionEngineLifecycle::test_engine_stop \
  -v -s -l --tb=long
```

### 4. Test Specific Module
```bash
# Test only execution module
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/unit/execution/ -v --cov=src/quantx/execution
```

### 5. Continuous Testing (Watch Mode)
```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
PYTHONPATH="$(pwd)/src" ptw tests/ -- -v
```

---

## 🔍 Coverage Report Details

### HTML Coverage Report

After running tests with `--cov-report=html`:

```bash
open htmlcov/index.html
```

**What you'll see**:
- Overall coverage percentage
- Per-file coverage breakdown
- Line-by-line highlighting:
  - 🟢 Green = Covered
  - 🔴 Red = Not covered
  - 🟡 Yellow = Partially covered (branches)

### Terminal Coverage Report

```
Coverage HTML written to dir htmlcov
Coverage XML written to file coverage.xml

Name                                           Stmts   Miss Branch BrPart  Cover
--------------------------------------------------------------------------------
src/quantx/execution/live_engine.py              235    182     42      0    19%
src/quantx/execution/position_sync.py            114     75     38      0    26%
src/quantx/execution/brokers/base.py             176     51     16      0    65%
--------------------------------------------------------------------------------
TOTAL                                           4625   3845   1116     13    14%
```

---

## 🛠️ Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```
E   ModuleNotFoundError: No module named 'quantx'
```
**Solution**: Set PYTHONPATH
```bash
export PYTHONPATH="$(pwd)/src"
# Or prefix every command with it
```

**2. Pytest not found**
```
bash: pytest: command not found
```
**Solution**: Install pytest
```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

**3. Import errors in tests**
```
E   ImportError: cannot import name 'Order'
```
**Solution**: Check the actual module structure
```bash
python3 -c "from quantx.execution.brokers.base import Order; print('OK')"
```

**4. Tests hanging**
```
# Test seems stuck
```
**Solution**: Add timeout
```bash
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v --timeout=30
pip install pytest-timeout  # If needed
```

---

## 📈 Best Practices

### 1. Run Tests Before Commit
```bash
# Create a pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
python3 -m pytest tests/ -v -x
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### 2. Organize Test Runs
```bash
# Create a test script
cat > run_tests.sh << 'EOF'
#!/bin/bash  
set -e

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src"

echo "🧪 Running QuantX Tests..."
echo ""

# Quick tests
echo "📋 Quick test run..."
python3 -m pytest tests/ -v -x

# Full coverage
echo ""
echo "📊 Running with coverage..."
python3 -m pytest tests/ -v \
  --cov=src/quantx \
  --cov-report=html \
  --cov-report=term-missing

echo ""
echo "✅ Tests complete!"
echo "📊 Coverage report: htmlcov/index.html"
EOF

chmod +x run_tests.sh
```

### 3. CI/CD Integration
```yaml
# .github/workflows/test.yml (already created)
# Runs automatically on push/PR
```

---

## 📊 Current Test Status

### Test Files
1. `tests/unit/execution/test_live_engine.py` - 10 tests
2. `tests/unit/execution/test_position_sync.py` - 7 tests

### Expected Results
```
17 tests total
7 passing (41%)
10 needing fixes
Coverage: ~14%
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v` |
| Run with coverage | `PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ --cov=src/quantx` |
| View HTML coverage | `open htmlcov/index.html` |
| Run specific file | `PYTHONPATH="$(pwd)/src" python3 -m pytest tests/unit/execution/test_live_engine.py -v` |
| Stop on first fail | `PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v -x` |
| Show print output | `PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v -s` |
| Debug mode | `PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v -s -l --tb=long` |

---

## 🚀 Try It Now!

```bash
# 1. Navigate to project
cd /Users/adii/Builds/Algo-Trading/QuantX

# 2. Run tests with coverage
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v --cov=src/quantx --cov-report=html --cov-report=term-missing

# 3. View results in browser
open htmlcov/index.html
```

**That's it!** You should see test results and coverage report.

---

**Updated**: December 27, 2025  
**Status**: Ready to use
