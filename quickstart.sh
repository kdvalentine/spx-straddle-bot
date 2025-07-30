#!/bin/bash

# SPX Straddle Bot - Quick Start Script
# This script guides you through the complete setup process

echo "======================================"
echo "SPX Straddle Bot - Quick Start Setup"
echo "======================================"
echo ""

# Step 1: Setup environment
echo "Step 1: Setting up Python environment..."
./scripts/setup_environment.sh

# Check if setup was successful
if [ ! -d "venv" ]; then
    echo "❌ Environment setup failed. Please check for errors above."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "======================================"
echo "Step 2: OpenD Installation"
echo "======================================"
echo ""
echo "You need to install OpenD (moomoo's API gateway)."
echo ""
echo "1. Download OpenD from: https://www.moomoo.com/download/OpenAPI"
echo "2. Install and run OpenD"
echo "3. Log into your moomoo account in OpenD"
echo "4. Keep OpenD running in the background"
echo ""
echo "Press Enter when OpenD is running and you're logged in..."
read

# Step 3: Get account info
echo ""
echo "======================================"
echo "Step 3: Discovering Your Account IDs"
echo "======================================"
echo ""
python scripts/get_account_info.py

echo ""
echo "======================================"
echo "Step 4: Configuration"
echo "======================================"
echo ""

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "✅ .env file created"
    echo ""
fi

echo "Now you need to edit the .env file with:"
echo "1. Your moomoo login credentials"
echo "2. The account ID shown above (copy the number displayed)"
echo ""
echo "Would you like to edit .env now? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    elif command -v code &> /dev/null; then
        code .env
    else
        echo "Please edit .env manually with your preferred editor"
    fi
fi

# Step 5: Test
echo ""
echo "======================================"
echo "Step 5: Testing Your Setup"
echo "======================================"
echo ""
echo "Ready to test your configuration?"
echo "Press Enter to run a connection test..."
read

python src/production_strategy_complete.py --check-only

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "If the test was successful, you can now run the bot:"
echo ""
echo "Paper trading (recommended):"
echo "  python src/production_strategy_complete.py --paper"
echo ""
echo "Live trading (use with caution):"
echo "  python src/production_strategy_complete.py"
echo ""
echo "For help, see the README.md file"