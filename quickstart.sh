#!/bin/bash

# QuantX Quick Start Helper Script
# This script helps you quickly run common examples

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Ensure we're in the right directory
cd "$(dirname "$0")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║                 QuantX Quick Start                       ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to run with PYTHONPATH
run_example() {
    local example_path="$1"
    local description="$2"
    
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Running:${NC} $description"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    PYTHONPATH="$(pwd)/src:$PYTHONPATH" python3 "$example_path"
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "\n${GREEN}✅ Example completed successfully!${NC}"
    else
        echo -e "\n${RED}❌ Example failed with exit code $exit_code${NC}"
        return $exit_code
    fi
}

# Show menu
echo "What would you like to run?"
echo ""
echo "Phase 1 - Backtesting:"
echo "  1) Fetch market data (Quick test - ~5 seconds)"
echo "  2) Complete backtest with strategy (~30 seconds)"
echo "  3) Strategy registry demo (~5 seconds)"
echo ""
echo "Phase 2 - Machine Learning:"
echo "  4) Feature engineering demo (~15 seconds)"
echo "  5) AI-powered strategy example (~1-2 minutes)"
echo "  6) Complete ML pipeline (~2-3 minutes)"
echo ""
echo "Phase 3 - Paper Trading:"
echo "  7) Paper trading basics (~10 seconds)"
echo "  8) Order management & risk controls (~15 seconds)"
echo ""
echo "Other:"
echo "  9) Run setup validation"
echo "  0) Exit"
echo ""
read -p "Enter your choice (0-9): " choice

case $choice in
    1)
        run_example "examples/fetch_data.py" "Fetch Market Data"
        ;;
    2)
        run_example "examples/complete_backtest.py" "Complete Backtest with MA Crossover Strategy"
        ;;
    3)
        run_example "examples/strategy_registry.py" "Strategy Registry Demo"
        ;;
    4)
        run_example "examples/ml/feature_engineering_demo.py" "Feature Engineering Demo"
        ;;
    5)
        run_example "examples/ml/ai_strategy_example.py" "AI-Powered Strategy"
        ;;
    6)
        run_example "examples/ml/complete_pipeline.py" "Complete ML Pipeline"
        ;;
    7)
        run_example "examples/live/paper_trading_example.py" "Paper Trading Basics"
        ;;
    8)
        run_example "examples/live/oms_risk_example.py" "Order Management & Risk Controls"
        ;;
    9)
        echo -e "\n${GREEN}Running setup validation...${NC}\n"
        python3 test_setup.py
        ;;
    0)
        echo -e "\n${BLUE}Goodbye! Happy trading! 📈${NC}\n"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Invalid choice. Please run the script again.${NC}\n"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Next Steps:${NC}"
echo -e "  • Run this script again to try other examples: ./quickstart.sh"
echo -e "  • Read the setup guide: cat SETUP_AND_RUN_GUIDE.md"
echo -e "  • View project docs: ls docs/"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
