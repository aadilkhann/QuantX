#!/bin/bash
# QuantX Test Runner
# Quick script to run tests with various options

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set PYTHONPATH
export PYTHONPATH="$(pwd)/src"

echo -e "${BLUE}🧪 QuantX Test Runner${NC}"
echo "========================================"
echo ""

# Show menu
echo "Select test option:"
echo "  1) Run all tests (quick)"
echo "  2) Run all tests with coverage report"
echo "  3) Run execution tests only"
echo "  4) Run specific test file"
echo "  5) View coverage report (HTML)"
echo "  6) Clean test cache"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo -e "${BLUE}Running all tests...${NC}"
        python3 -m pytest tests/ -v
        ;;
    2)
        echo -e "${BLUE}Running tests with coverage...${NC}"
        python3 -m pytest tests/ -v \
            --cov=src/quantx \
            --cov-report=html \
            --cov-report=term-missing
        echo ""
        echo -e "${GREEN}✅ Coverage report generated!${NC}"
        echo -e "Open: ${YELLOW}htmlcov/index.html${NC}"
        ;;
    3)
        echo -e "${BLUE}Running execution tests...${NC}"
        python3 -m pytest tests/unit/execution/ -v \
            --cov=src/quantx/execution \
            --cov-report=term-missing
        ;;
    4)
        echo ""
        echo "Available test files:"
        find tests/ -name "test_*.py" -type f | nl
        echo ""
        read -p "Enter file path: " filepath
        echo -e "${BLUE}Running $filepath...${NC}"
        python3 -m pytest "$filepath" -v -s
        ;;
    5)
        echo -e "${BLUE}Opening coverage report...${NC}"
        if [ -f "htmlcov/index.html" ]; then
            open htmlcov/index.html || xdg-open htmlcov/index.html 2>/dev/null
        else
            echo -e "${RED}❌ Coverage report not found!${NC}"
            echo "Run option 2 first to generate coverage report."
        fi
        ;;
    6)
        echo -e "${YELLOW}Cleaning test cache...${NC}"
        rm -rf .pytest_cache __pycache__ htmlcov .coverage
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name "*.pyc" -exec rm -f {} + 2>/dev/null || true
        echo -e "${GREEN}✅ Cache cleaned!${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done!${NC}"
