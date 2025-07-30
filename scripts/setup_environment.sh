#!/bin/bash

# SPX Straddle Bot - Environment Setup Script
# This script helps set up the Python environment and dependencies

echo "======================================"
echo "SPX Straddle Bot - Environment Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✓ Python $python_version is installed (>= $required_version required)"
else
    echo "✗ Python $python_version is too old. Please install Python $required_version or newer."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "✓ .env file created"
    echo ""
    echo "IMPORTANT: Edit .env file with your moomoo credentials before running the bot!"
else
    echo "✓ .env file already exists"
fi

# Create logs directory
echo ""
if [ ! -d "logs" ]; then
    echo "Creating logs directory..."
    mkdir -p logs
    echo "✓ Logs directory created"
else
    echo "✓ Logs directory already exists"
fi

echo ""
echo "======================================"
echo "Setup completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Install OpenD from https://www.moomoo.com/download/OpenAPI"
echo "2. Run OpenD and log into your moomoo account"
echo "3. Run: python scripts/get_account_info.py to find your account IDs"
echo "4. Edit .env file with your credentials and account ID"
echo "5. Test with: python src/production_strategy_complete.py --check-only"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "source venv/bin/activate"
echo ""