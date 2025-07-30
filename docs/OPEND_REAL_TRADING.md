# OpenD Configuration for Real Trading

This guide explains how to configure OpenD for live trading with real money.

## Important Warning ⚠️

**Real trading uses actual money. Ensure you understand the risks and have tested thoroughly with paper trading first.**

## OpenD Trading Modes

OpenD can operate in two modes:
1. **Paper Trading** - Uses simulated money (default)
2. **Real Trading** - Uses actual money

## Switching to Real Trading Mode

### Method 1: OpenD GUI Configuration

1. **Launch OpenD**
   - macOS: Open `/Applications/OpenD.app`
   - Windows: Run `OpenD.exe`
   - Linux: Run `./OpenD`

2. **Login to your moomoo account**
   - Enter your account credentials
   - Complete 2FA if required

3. **Access Account Settings**
   - Look for account/environment settings
   - You should see both paper and real accounts listed

4. **Verify Real Account Access**
   - Real accounts will show actual balances
   - Paper accounts show simulated balances (usually $1M)

### Method 2: Configuration File

OpenD stores configuration in:
- macOS: `~/Library/Application Support/OpenD/`
- Windows: `%APPDATA%\OpenD\`
- Linux: `~/.OpenD/`

**Note**: Direct config file editing is not recommended. Use the GUI.

## Verifying Real Account Access

### 1. Run Account Discovery
```bash
python scripts/get_account_info.py
```

You should see output like:
```
💰 REAL TRADING ACCOUNTS (real money):
----------------------------------------
Account ID: 283445331390335663
Type: CASH

Account ID: 283445329034551681
Type: MARGIN
```

### 2. Check Account Balances
Real accounts will show your actual balance:
```
REAL Account 283445331390335663:
  Cash: $41,104.06
  Total Assets: $41,104.06
```

Paper accounts typically show:
```
PAPER Account 2043264:
  Cash: $1,000,000.00
  Total Assets: $1,000,000.00
```

## Bot Configuration for Real Trading

### 1. Update .env file
```bash
# Set to REAL for live trading
TRADING_ENV=REAL

# Use your real account ID (from account discovery)
MOOMOO_ACCOUNT_ID=283445331390335663

# Ensure trade password is set
MOOMOO_TRADE_PWD=your_trade_password
```

### 2. Verify with --check-only
```bash
python src/production_strategy_complete.py --check-only
```

Should show:
```
Using preferred REAL account: 283445331390335663 (Type: CASH)
Account refreshed - Cash: $41,104.50, Buying Power: $0.00
```

## Safety Checklist

Before enabling real trading:

1. ✅ **Paper Trading Success**
   - Run bot in paper mode for at least 1 week
   - Verify all trades execute as expected
   - Check position sizing is correct

2. ✅ **Risk Settings**
   ```bash
   # In .env - start conservative
   MAX_RISK_PCT=0.01  # 1% to start
   ```

3. ✅ **Account Verification**
   - Correct account ID in .env
   - Sufficient balance for trading
   - Trade password is correct

4. ✅ **Test Connection**
   ```bash
   # Must show real account and balance
   python src/production_strategy_complete.py --check-only
   ```

5. ✅ **Monitor First Trades**
   - Watch the first few live trades closely
   - Verify orders match expectations
   - Check position sizes are appropriate

## Troubleshooting

### "No REAL account found"
- Ensure OpenD is logged into your real account
- Check MOOMOO_TRADE_PWD is correct
- Verify SecurityFirm.FUTUINC is used (automatic in latest version)

### "Trade unlock failed"
- Trade password is incorrect
- Account may not have trading permissions
- OpenD may be in paper-only mode

### Can only see paper accounts
1. OpenD is not configured for real trading
2. Not logged into real account in OpenD
3. Trade password not provided or incorrect

## Switching Back to Paper

To switch back to paper trading:
```bash
# In .env
TRADING_ENV=PAPER
MOOMOO_ACCOUNT_ID=2043264  # Your paper account ID
```

## Security Best Practices

1. **Never share your .env file** - Contains passwords
2. **Use strong passwords** - Especially trade password
3. **Enable 2FA** - On your moomoo account
4. **Monitor account** - Check for unexpected trades
5. **Start small** - Use minimal position sizes initially

## Emergency Stop

To immediately stop all trading:
1. Stop the bot process (Ctrl+C)
2. Close OpenD
3. Log into moomoo app and check positions
4. Cancel any open orders manually if needed

## Support

- Moomoo Support: Available in-app
- API Documentation: https://openapi.moomoo.com/
- Never share credentials when seeking help