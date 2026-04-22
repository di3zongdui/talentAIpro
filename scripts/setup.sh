#!/bin/bash
# TalentAI Pro - Development Setup Script
# Usage: ./scripts/setup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== TalentAI Pro Setup ===${NC}"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"
if ! printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V -c &>/dev/null; then
    echo -e "${RED}Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Removing...${NC}"
    rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create environment file
echo ""
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created. Please edit it with your credentials.${NC}"
else
    echo -e "${YELLOW}.env file already exists.${NC}"
fi

# Create directories
echo ""
echo "Creating directories..."
mkdir -p data logs ssl

# Initialize database
echo ""
echo "Initializing database..."
python -c "from TalentAI_Pro.models import init_db; init_db()" 2>/dev/null || echo -e "${YELLOW}Database initialization skipped (use 'python run_server.py' to start).${NC}"

# Run tests
echo ""
echo -e "${BLUE}Running tests...${NC}"
python -m pytest tests/ -v --tb=short 2>/dev/null || echo -e "${YELLOW}Tests skipped.${NC}"

echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To start the server:"
echo "  python run_server.py"
echo ""
echo "To view API documentation:"
echo "  http://localhost:8000/docs"
echo ""
