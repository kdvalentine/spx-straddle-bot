# SPX Straddle Trading Bot

A production-ready automated trading bot for SPX index options straddles with comprehensive risk management and safety features.

## Overview

This bot automatically trades SPX straddles (simultaneous purchase of at-the-money calls and puts) with the following features:

- **Automated Strike Selection**: Finds optimal ATM strikes based on current SPX price
- **Smart Order Execution**: Dynamic pricing based on bid-ask spreads
- **Risk Management**: Position sizing based on account risk limits
- **Market Safety**: Trading hours validation and holiday calendar
- **Comprehensive Logging**: Trade tracking and performance monitoring

## Quick Start

**📚 New to coding?** See the [Simple Setup Guide](SIMPLE_SETUP_GUIDE.md) for step-by-step instructions!

**Easiest way**: Run the interactive setup script:
```bash
./quickstart.sh  # Mac/Linux
quickstart.bat   # Windows
```

**Manual steps**:
1. **Install dependencies**: `./scripts/setup_environment.sh`
2. **Install and run OpenD**: Download from [moomoo OpenAPI](https://www.moomoo.com/download/OpenAPI)
3. **Get your account ID**: `python scripts/get_account_info.py`
4. **Configure**: Edit `.env` with your credentials
5. **Test**: `python src/production_strategy_complete.py --check-only`
6. **Run**: `python src/production_strategy_complete.py --paper`

## Prerequisites

### System Requirements
- macOS, Linux, or Windows
- Python 3.8 or higher
- Internet connection
- Moomoo trading account with API access enabled

### Required Software
1. **Python 3.8+**
   ```bash
   python3 --version  # Should show 3.8 or higher
   ```

2. **Moomoo OpenD Gateway**
   - Download from: https://www.moomoo.com/download/OpenAPI
   - Required for API connectivity
   - Must be running before starting the bot

3. **Moomoo Account Requirements**
   - Active moomoo account (paper or live)
   - API trading enabled in account settings
   - Login credentials (account number and password)
   - Trade password (essential for real account access)

## Installation

### 1. Clone or Download the Repository
```bash
# If using git
git clone <repository-url>
cd spx-straddle-bot

# Or download and extract the ZIP file
```

### 2. Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and Configure OpenD

#### macOS:
1. Download OpenD from https://www.moomoo.com/download/OpenAPI
2. Extract the downloaded file
3. Move OpenD.app to your Applications folder
4. Launch OpenD.app
5. Log into your moomoo account in OpenD
6. Keep it running in the background

#### Windows:
1. Download OpenD from https://www.moomoo.com/download/OpenAPI
2. Extract to a folder (e.g., C:\OpenD)
3. Run OpenD.exe
4. Log into your moomoo account in OpenD
5. Keep it running in the background

#### Linux:
```bash
# Run the provided script
./scripts/install_opend_linux.sh
```

### 5. Create Initial Configuration
```bash
# Copy the template
cp .env.template .env
```

### 6. Get Your Moomoo Account IDs

Now that OpenD is running and you're logged in, discover your account IDs:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the account discovery tool
python scripts/get_account_info.py
```

This will:
- Connect to OpenD and find all your accounts
- Show account IDs for both paper and real accounts
- Display current balances
- Tell you exactly which ID to use

**Alternative Method**: If the script doesn't work, you can find account IDs manually in the moomoo app under Account > Account Management.

### 7. Complete Configuration

Edit the .env file with your credentials and the account ID from step 6:

```bash
# Edit .env with your credentials
# Use your favorite editor (nano, vim, code, etc.)
nano .env
```

**Required settings:**
- `MOOMOO_LOGIN_ACCOUNT`: Your moomoo account number
- `MOOMOO_LOGIN_PWD`: Your moomoo login password
- `MOOMOO_TRADE_PWD`: Your moomoo trade password (required for real accounts)
- `MOOMOO_ACCOUNT_ID`: The account ID from step 6
- `TRADING_ENV`: Set to "PAPER" for testing, "REAL" for live trading

**Important**: The trade password is essential for accessing real accounts. Without it, you'll only see paper trading accounts.

## Usage

### Test Your Setup (Recommended First Step)
```bash
# Check market status and account without trading
python src/production_strategy_complete.py --check-only
```

This will verify:
- OpenD connection
- Account credentials
- Current SPX price
- Market hours status
- Account balance

### Paper Trading Mode (Recommended for Testing)
```bash
# Ensure TRADING_ENV=PAPER in your .env file
python src/production_strategy_complete.py --paper
```

### Live Trading Mode
```bash
# WARNING: This uses real money!
# Ensure TRADING_ENV=REAL in your .env file
python src/production_strategy_complete.py
```

## Configuration Options

### Risk Management (.env file)
- `MAX_RISK_PCT`: Maximum percentage of account to risk per trade (default: 0.15 = 15%)
- `MAX_SPREAD_PCT`: Maximum acceptable bid-ask spread (default: 30%)
- `ORDER_TIMEOUT_S`: Seconds to wait for order fills (default: 30)

### Trading Parameters
- `EXECUTION_TIME`: When to run the bot (default: 15:45:00 = 3:45 PM)
- **Note**: 0DTE options expire at end of day - no stop loss needed

## Safety Features

1. **Market Hours Validation**: Only trades during US market hours
2. **Holiday Calendar**: Skips US market holidays
3. **Capital Validation**: Checks buying power before trading
4. **Position Sizing**: Limits risk to configured percentage
5. **Spread Validation**: Rejects options with excessive spreads
6. **Order Confirmation**: Waits for fill confirmation
7. **Two-Leg Coordination**: Cancels call if put order fails

## Monitoring

### Log Files
- **General logs**: `logs/spx_straddle_bot.log`
- **Trade records**: `logs/trades.json`

### Log Rotation
- Logs rotate at 10MB
- Keeps 5 backup files
- JSON trade logs for analysis

## Troubleshooting

### "Cannot connect to OpenD"
1. Ensure OpenD is running
2. Check OpenD shows "API Ready" status
3. Verify OPEND_HOST and OPEND_PORT in .env

### "Invalid account credentials" or "Only seeing paper accounts"
1. Double-check account number and password
2. Verify your trade password is correct in .env
3. Ensure API trading is enabled in moomoo app
4. Try logging into moomoo app first
5. For real accounts, MOOMOO_TRADE_PWD must be set

### "Cannot obtain valid SPX price"
1. Check internet connection
2. Verify market is open
3. Try again in a few seconds

### "Insufficient buying power"
1. Check account balance
2. Reduce MAX_RISK_PCT in .env
3. Ensure no pending orders

## Best Practices

1. **Always test with paper trading first**
2. **Start with small position sizes**
3. **Monitor the first few trades closely**
4. **Run 10-30 minutes before market close for 0DTE**
5. **Keep OpenD updated to latest version**
6. **Review logs regularly**

## Additional Documentation

- **Simple Setup Guide**: See `SIMPLE_SETUP_GUIDE.md` (for beginners!)
- **How It Works**: See `docs/HOW_IT_WORKS.md` (visual guide)
- **Strategy Details**: See `docs/PRODUCTION_STRATEGY_COMPLETE.md`
- **Configuration Flow**: See `docs/CONFIGURATION_FLOW.md`
- **Real Trading Setup**: See `docs/OPEND_REAL_TRADING.md`
- **Scheduling/Automation**: See `docs/SCHEDULING.md`
- **Testing Checklist**: See `docs/TEST_CHECKLIST.md`

## Support

## Disclaimer

**IMPORTANT**: This software is for educational purposes. Trading options involves substantial risk of loss. Past performance does not guarantee future results. Always understand the risks before trading with real money.

## License

This project is provided as-is without warranty. Use at your own risk.