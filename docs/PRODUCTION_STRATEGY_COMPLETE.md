# Production SPX Straddle Bot - Complete Implementation

## Overview

This document describes the complete production-ready SPX straddle trading bot that incorporates all safety and optimization phases (1-4). The bot is designed for reliable, automated trading with comprehensive risk management and monitoring.

## Trading Strategy

### 0DTE (Zero Days to Expiration) Straddles
- **Entry**: Buy ATM call and put options expiring same day
- **Exit**: Hold until market close (no stop loss needed)
- **Rationale**: 0DTE options expire worthless at end of day if not profitable
- **Risk**: Limited to premium paid (positions cannot lose more than initial cost)
- **Profit**: Captures large intraday moves in either direction

### Why No Stop Loss?
- 0DTE options have maximum loss built-in (the premium paid)
- Options expire at 4:00 PM ET automatically
- Stop losses can trigger on normal volatility, missing potential profitable moves
- The strategy profits from significant moves in either direction

## Architecture

### Core Components

1. **Connection Management** - Resilient API connections with retry logic
2. **Market Validation** - Timezone-aware hours and holiday checking  
3. **Price Discovery** - Multiple data sources with validation
4. **Position Management** - Risk-based sizing and existing position checks
5. **Order Execution** - Smart pricing with fill monitoring
6. **Logging & Monitoring** - Comprehensive trade and performance tracking

## Feature Implementation by Phase

### Phase 1: Critical Safety Features ✅

#### 1.1 SPX Price Validation
- **No hardcoded fallback** - fails safely if price unavailable
- Multiple data sources (moomoo first, yfinance backup)
- Price range validation (3000-7000)
- Retry logic with exponential backoff

#### 1.2 Strike Selection
- Dynamic intervals based on SPX level:
  - SPX < 4000: $5 intervals
  - SPX 4000-5000: $10 intervals  
  - SPX > 5000: $25 intervals
- Searches ±10 strikes from ATM

#### 1.3 Market Hours Validation
- Full timezone awareness (America/New_York)
- Trading hours: 9:30 AM - 4:00 PM ET
- Weekend detection
- US market holiday calendar for 2025
- Proper expiry calculation considering timezone

#### 1.4 Capital Validation
- Pre-trade buying power check
- Account balance refresh before orders
- Total cost estimation with buffers
- Prevents over-leveraging

### Phase 2: Order Management & Position Sizing ✅

#### 2.1 Order Fill Confirmation
```python
def wait_for_fill(self, order_id, timeout=30):
    # Monitors order status until filled or timeout
    # Handles partial fills
    # Returns fill status and average price
```

#### 2.2 Position Sizing
- Risk-based sizing (default 15% of account per trade, allows ~3 positions)
- Considers both risk limit and buying power
- Minimum 1 contract if affordable
- Formula: `min(risk_contracts, buying_power_contracts)`

#### 2.3 Smart Order Pricing
```python
def calculate_order_price(self, bid, ask, is_urgent=False):
    # Tight spreads (<1%): 60% of spread from bid
    # Normal spreads (1-5%): 75% of spread from bid
    # Wide spreads (>5%): 1% over ask
```

### Phase 3: Robustness & Reliability ✅

#### 3.1 Connection Resilience
- Automatic retry on connection failure (default 3 attempts)
- Connection health checks
- Graceful error handling
- Clean connection closure

#### 3.2 Existing Position Detection
```python
def check_existing_positions(self):
    # Queries all SPXW positions
    # Logs existing holdings
    # Can be extended to close/adjust positions
```

#### 3.3 Comprehensive Logging
- Rotating file logs (10MB max, 5 backups)
- Structured trade logs in JSON format
- Console and file output
- Trade performance tracking

### Phase 4: Optimization & Analytics ✅

#### 4.1 Liquidity-Based Selection
```python
# Liquidity score calculation:
liquidity_score = (volume_score + spread_score * 2) / 3

# Selection considers both:
# - Distance from ATM (primary)
# - Liquidity score (secondary)
```

#### 4.2 Dynamic Order Pricing
- Adjusts aggressiveness based on:
  - Spread width
  - Fill urgency
  - Retry attempt
- Progressive pricing on retries

#### 4.3 Performance Monitoring
- Trade result tracking
- JSON trade logs for analysis
- Integration with position manager
- Real-time account metrics

## Configuration

### Environment Variables (.env)
```bash
# Trading Environment
TRADING_ENV=REAL  # or SIMULATE for paper trading

# Connection
MOOMOO_HOST=127.0.0.1
MOOMOO_PORT=11111

# Risk Management
MAX_RISK_PCT=0.15  # 15% of account per trade (allows ~3 positions)
MAX_SPREAD_PCT=30  # Maximum acceptable bid-ask spread (SPX options can have wider spreads)

# Order Management
ORDER_TIMEOUT_S=30
PRICE_BUFFER_PCT=2.0
CONNECTION_RETRIES=3
```

### Command Line Options
```bash
# Live trading (default)
python production_strategy_complete.py

# Paper trading mode
python production_strategy_complete.py --paper

# Check market and positions only
python production_strategy_complete.py --check-only
```

## Trade Execution Flow

1. **Pre-Trade Validation**
   - Market hours check
   - Holiday calendar check
   - Account balance refresh
   - Existing position check

2. **Strike Selection**
   - Fetch current SPX price
   - Calculate expiry (next Friday)
   - Search strikes with dynamic intervals
   - Batch fetch all option quotes

3. **Straddle Analysis**
   - Validate bid/ask spreads
   - Calculate liquidity scores
   - Select best combination of ATM + liquidity

4. **Position Sizing**
   - Calculate max risk (15% of account)
   - Check buying power
   - Determine optimal contract count

5. **Order Execution**
   - Smart initial pricing
   - Place call order
   - Place put order (cancel call if fails)
   - Monitor fills with timeout
   - Progressive repricing on retries

6. **Post-Trade**
   - Log complete trade details
   - Update position tracking
   - Performance metrics

## Risk Management

### Account Limits
- Maximum 15% of account value per trade (allows ~3 positions)
- Buying power validation
- Minimum position size checks

### Order Safety
- Two-leg coordination (cancel first if second fails)
- Fill confirmation before proceeding
- Timeout protection
- Smart pricing to avoid overpaying

### Market Safety
- No trading outside market hours
- Holiday calendar awareness
- Spread reasonableness checks
- Volume/liquidity requirements

## Monitoring & Analysis

### Log Files
- `logs/spx_straddle_bot.log` - General operation logs
- `logs/trades.json` - Structured trade records

### Trade Record Format
```json
{
  "timestamp": "2025-07-23T15:45:30",
  "spx_price": 5150.25,
  "strike": 5150,
  "call_code": "US.SPXW250725C5150000",
  "put_code": "US.SPXW250725P5150000",
  "call_fill_price": 15.25,
  "put_fill_price": 14.80,
  "contracts": 2,
  "total_cost": 6010.00,
  "status": "filled",
  "notes": "Liquidity score: 85.3"
}
```

## Troubleshooting

### Common Issues

1. **"Cannot obtain valid SPX price"**
   - Check internet connection
   - Verify yfinance is working
   - Check moomoo connection

2. **"No valid straddles found"**
   - May indicate options are not available for expiry
   - Check if market is near close
   - Verify option codes format

3. **"Insufficient buying power"**
   - Account may have pending settlements
   - Existing positions consuming buying power
   - Need to adjust position sizing

4. **Order Failures**
   - Check if market is volatile
   - Spreads may be too wide
   - Consider increasing price buffer

## Best Practices

1. **Testing**
   - Always test in paper mode first
   - Run `--check-only` to verify setup
   - Monitor first few live trades closely

2. **Scheduling**
   - Best run 10-30 minutes before close
   - Avoid first/last minutes of trading
   - Consider market volatility

3. **Monitoring**
   - Check logs regularly
   - Review trade performance
   - Adjust parameters based on results

4. **Maintenance**
   - Update holiday calendar yearly
   - Review risk parameters monthly
   - Archive old log files

## Version History

- **Phase 1**: Critical safety fixes (SPX price, strikes, hours, capital)
- **Phase 2**: Order management (fills, sizing, smart pricing)
- **Phase 3**: Robustness (retry, positions, logging)
- **Phase 4**: Optimization (liquidity, dynamic pricing, monitoring)

## Support

For issues or questions:
1. Check logs for detailed error messages
2. Run with `--check-only` to diagnose
3. Verify all prerequisites are installed
4. Ensure moomoo desktop app is running

---

*Last Updated: July 2025*
*Version: 1.0 (Complete Production)*