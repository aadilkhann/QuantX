#!/bin/bash
# Start QuantX API Server

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src"

echo "🚀 Starting QuantX API Server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop"
echo ""

python3 -m uvicorn quantx.api.main:app --reload --host 0.0.0.0 --port 8000
