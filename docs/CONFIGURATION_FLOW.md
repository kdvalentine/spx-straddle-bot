# Configuration Flow Explanation

This document explains how configuration values flow from your `.env` file to the bot's execution.

## Configuration Hierarchy

The bot uses a three-tier configuration system:

1. **Environment Variables** (.env file) - Your custom settings
2. **LocalConfig defaults** - Fallback values in local_config.py
3. **Production defaults** - Ultimate fallbacks in production_strategy_complete.py

## How It Works

### Step 1: Environment Variables
When you set values in your `.env` file:
```bash
MAX_RISK_PCT=0.20  # Override to 20%
MAX_SPREAD_PCT=35  # Override to 35%
```

### Step 2: LocalConfig Loads Environment
The `local_config.py` creates a global `config` object:
```python
# local_config.py
class LocalConfig:
    def __init__(self):
        # Loads from .env with defaults
        self.max_risk_pct = float(os.getenv('MAX_RISK_PCT', '0.15'))
        self.max_spread_pct = float(os.getenv('MAX_SPREAD_PCT', '30'))
    
    def get(self, key, default=None):
        # Dictionary-style access
        return getattr(self, key, default)

# Global instance
config = LocalConfig()
```

### Step 3: Production Strategy Uses Config
The `production_strategy_complete.py` imports and uses the config:
```python
# production_strategy_complete.py
from local_config import config

# Constants as ultimate fallbacks
DEFAULT_MAX_RISK_PCT = 0.15
DEFAULT_MAX_SPREAD_PCT = 30.0

class SPXStraddleStrategy:
    def __init__(self):
        # Try config first, then use defaults
        self.max_risk_pct = config.get('max_risk_pct', DEFAULT_MAX_RISK_PCT)
        self.max_spread_pct = config.get('max_spread_pct', DEFAULT_MAX_SPREAD_PCT)
```

## Value Resolution Order

When the bot needs a configuration value:

1. **First**: Checks if you set it in `.env` file
2. **Second**: Uses LocalConfig's default if not in .env
3. **Third**: Uses production constant if not in LocalConfig

### Example: MAX_RISK_PCT

1. If `.env` has `MAX_RISK_PCT=0.20` → Uses 0.20 (20%)
2. If `.env` doesn't have it → Uses LocalConfig default 0.15 (15%)
3. If LocalConfig fails → Uses production default 0.15 (15%)

## Current Default Values

| Setting | .env Variable | LocalConfig Default | Production Default | Purpose |
|---------|--------------|--------------------|--------------------|---------|
| Max Risk % | MAX_RISK_PCT | 15% | 15% | Max % of account per trade |
| Max Spread % | MAX_SPREAD_PCT | 30% | 30% | Max bid-ask spread allowed |
| Order Timeout | ORDER_TIMEOUT_S | 30s | 30s | Time to wait for fills |
| Price Buffer | PRICE_BUFFER_PCT | 2% | 2% | Initial order buffer |
| Connection Retries | CONNECTION_RETRIES | 3 | 3 | API retry attempts |

## Checking Active Values

To see what values are actually being used:

1. **Check your .env file** - Your overrides
2. **Run with --check-only** - Shows loaded configuration
3. **Check logs** - LocalConfig logs risk settings on startup

## Best Practices

1. **Use .env for customization** - Don't edit the Python files
2. **Start conservative** - Test with lower risk percentages first
3. **Document changes** - Add comments in your .env file
4. **Version control** - Never commit .env (only .env.template)

## Example .env Customization

```bash
# Custom risk settings for my account
MAX_RISK_PCT=0.10      # Lower risk: 10% instead of 15%
MAX_SPREAD_PCT=25      # Tighter spreads: 25% instead of 30%
ORDER_TIMEOUT_S=45     # More time for fills: 45s instead of 30s
```