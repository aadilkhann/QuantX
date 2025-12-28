# Quick Test Commands

## 🚀 Easiest Way - Use the Test Runner Script

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
./run_tests.sh
```

This will show you a menu with options!

---

## 📋 Manual Commands

### 1. Run All Tests (Quick)
```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v
```

**Expected Output**:
```
collected 17 items

tests/unit/execution/test_live_engine.py::test_engine_initialization PASSED [  5%]
tests/unit/execution/test_live_engine.py::test_engine_start PASSED [ 11%]
...
====== 7 passed, 10 failed in 2.34s ======
```

### 2. Run with Coverage Report
```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v \
  --cov=src/quantx \
  --cov-report=html \
  --cov-report=term-missing
```

Then open the report:
```bash
open htmlcov/index.html
```

### 3. Run Just Execution Tests
```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/unit/execution/ -v
```

---

## 📊 What You'll See

### Test Results
```
✅ PASSED - Test succeeded
❌ FAILED - Test failed
```

### Current Status
- **17 tests** total
- **7 passing** (41%)
- **10 need fixes** (minor issues)
- **Coverage**: 14%

### Coverage Report
After running with `--cov-report=html`, open `htmlcov/index.html` to see:
- Which lines are tested (green)
- Which lines need tests (red)
- Overall coverage percentage

---

## 🎯 Recommended First Run

```bash
# Navigate to project
cd /Users/adii/Builds/Algo-Trading/QuantX

# Run tests with coverage and HTML report
PYTHONPATH="$(pwd)/src" python3 -m pytest tests/ -v \
  --cov=src/quantx \
  --cov-report=html \
  --cov-report=term-missing

# Open the beautiful HTML report
open htmlcov/index.html
```

This gives you:
1. ✅ Test results in terminal
2. 📊 Coverage percentage
3. 🌐 Interactive HTML report

---

## 💡 Tips

1. **First time?** Just run:
   ```bash
   ./run_tests.sh
   ```
   Choose option 2 for full coverage report.

2. **Quick check?** Run option 1 for fast results.

3. **See what's covered?** Use option 5 to view the HTML report.

---

**For full details**: See `docs/TESTING_GUIDE.md`
