# Quick Fix: Install FastAPI Dependencies

The error shows FastAPI is not installed in your current Python environment.

## Fix (Run these commands)

```bash
# Activate your virtual environment (if not already)
source venv/bin/activate

# Install FastAPI and dependencies
pip install fastapi "uvicorn[standard]" websockets python-multipart

# Verify installation
python3 -m pip list | grep -i fastapi
```

Expected output:
```
fastapi    0.115.x
```

## Then Try Again

```bash
./start_api.sh
```

---

## Alternative: Install ALL Requirements

```bash
pip install -r requirements.txt
```

This will install everything including FastAPI.

---

## Still Having Issues?

Make sure you've activated the venv FIRST:
```bash
# Check if venv is active (you should see (venv) in your prompt)
which python3

# Should show something like:
# /Users/adii/Builds/Algo-Trading/QuantX/venv/bin/python3
```

If not in venv:
```bash
source venv/bin/activate
# Then try pip install again
```
