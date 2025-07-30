#!/bin/bash

# Quick start script for SPX Straddle Bot

echo "Starting SPX Straddle Bot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./scripts/setup_environment.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.template to .env and add your credentials."
    exit 1
fi

# Parse command line arguments
if [ "$1" == "--check-only" ]; then
    echo "Running in check-only mode..."
    python src/production_strategy_complete.py --check-only
elif [ "$1" == "--paper" ]; then
    echo "Running in paper trading mode..."
    python src/production_strategy_complete.py --paper
elif [ "$1" == "--help" ]; then
    echo "Usage: ./scripts/run_bot.sh [options]"
    echo "Options:"
    echo "  --check-only  Check market and account status without trading"
    echo "  --paper       Run in paper trading mode"
    echo "  --help        Show this help message"
    echo "  (no options)  Run in mode specified by .env file"
else
    echo "Running bot with settings from .env file..."
    python src/production_strategy_complete.py
fi