# Scheduling the SPX Straddle Bot

This guide explains how to automatically run the bot at specific times.

## Recommended Schedule

For 0DTE (same-day expiry) SPX straddles, the optimal time is typically:
- **3:30-3:45 PM ET** - Allows time to enter positions before close
- **Weekdays only** - Markets closed on weekends
- **Skip holidays** - Bot checks holiday calendar automatically

## Linux/macOS - Using Cron

### 1. Open crontab editor
```bash
crontab -e
```

### 2. Add cron job

**IMPORTANT**: Cron uses the system timezone. If your server is not in ET, adjust the hour accordingly.

```bash
# Run SPX straddle bot at 3:45 PM ET every weekday
# This example assumes system is in ET timezone
45 15 * * 1-5 cd /path/to/spx-straddle-bot && /path/to/spx-straddle-bot/venv/bin/python src/production_strategy_complete.py >> logs/cron.log 2>&1
```

**Time zone conversion examples:**
- 3:45 PM ET = 15:45 ET
- 3:45 PM ET = 12:45 PM PT (PST/PDT)
- 3:45 PM ET = 20:45 UTC (during EST)
- 3:45 PM ET = 19:45 UTC (during EDT)

### 3. Complete working example

Replace `/home/youruser/spx-straddle-bot` with your actual path:

```bash
# For ET timezone system
45 15 * * 1-5 cd /home/youruser/spx-straddle-bot && source venv/bin/activate && python src/production_strategy_complete.py >> logs/cron.log 2>&1

# For PT timezone system (12:45 PM PT = 3:45 PM ET)
45 12 * * 1-5 cd /home/youruser/spx-straddle-bot && source venv/bin/activate && python src/production_strategy_complete.py >> logs/cron.log 2>&1

# For UTC system (20:45 UTC = 3:45 PM ET during winter)
45 20 * * 1-5 cd /home/youruser/spx-straddle-bot && source venv/bin/activate && python src/production_strategy_complete.py >> logs/cron.log 2>&1
```

### 4. Verify your timezone
```bash
# Check system timezone
timedatectl | grep "Time zone"  # Linux
date +%Z                         # macOS/Linux

# The bot internally uses ET for market hours checking
```

### 5. Important considerations
- Use absolute paths (not ~ or relative paths)
- Ensure OpenD is running before scheduled time
- The bot handles market hours/holidays internally
- Cron doesn't load your .bashrc/.profile - paths must be explicit
- The .env file MUST be in the bot directory (cron runs from there with `cd`)

## Windows - Using Task Scheduler

### 1. Create batch file
Create `run_bot.bat`:
```batch
@echo off
cd C:\path\to\spx-straddle-bot
call venv\Scripts\activate
python src\production_strategy_complete.py >> logs\scheduled.log 2>&1
```

### 2. Set up Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 3:45 PM
4. Set action: Start program → Select your .bat file
5. Configure for weekdays only in Advanced settings

## Cloud Scheduling Options

### AWS EventBridge (formerly CloudWatch Events)
```python
# Example Lambda function
import subprocess

def lambda_handler(event, context):
    # Ensure OpenD is running on EC2
    # Execute bot
    subprocess.run(['python', '/path/to/bot/src/production_strategy_complete.py'])
```

### GitHub Actions
```yaml
name: Run Trading Bot
on:
  schedule:
    # Run at 3:45 PM ET (7:45 PM UTC during EDT)
    - cron: '45 19 * * 1-5'
    
jobs:
  trade:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run bot
        run: |
          python src/production_strategy_complete.py
```

## Monitoring & Alerts

### Email notifications on Linux
```bash
# Add to crontab for email on failure
45 15 * * 1-5 /path/to/run_bot.sh || echo "Bot failed" | mail -s "SPX Bot Error" your@email.com
```

### Log monitoring
```bash
# Check recent executions
tail -f logs/spx_straddle_bot.log

# Check cron logs
grep CRON /var/log/syslog  # Ubuntu/Debian
grep CRON /var/log/cron    # CentOS/RHEL
```

## Pre-execution Checklist

Before scheduling, ensure:
1. ✅ OpenD starts automatically or is always running
2. ✅ .env file has correct credentials
3. ✅ Test with --check-only flag first
4. ✅ Sufficient account balance
5. ✅ Logs directory is writable

## OpenD Auto-start

### Linux systemd service
Create `/etc/systemd/system/opend.service`:
```ini
[Unit]
Description=Moomoo OpenD Gateway
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/OpenD
ExecStart=/path/to/OpenD/OpenD
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable with: `sudo systemctl enable opend.service`

### macOS LaunchAgent
Create `~/Library/LaunchAgents/com.moomoo.opend.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.moomoo.opend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/OpenD.app/Contents/MacOS/OpenD</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load with: `launchctl load ~/Library/LaunchAgents/com.moomoo.opend.plist`

## Testing Your Schedule

### Quick Test (Recommended)
First, test with a schedule 5 minutes in the future:

```bash
# Get current time
date

# Add test cron job (if it's 2:30 PM, set for 2:35 PM)
crontab -e
# Add: 35 14 * * * cd /home/youruser/spx-straddle-bot && source venv/bin/activate && python src/production_strategy_complete.py --check-only >> logs/test.log 2>&1

# Wait 5 minutes, then check
tail -f logs/test.log

# Remove test entry after verification
crontab -e
```

### Verify the schedule worked:
1. ✅ Log file created with timestamp
2. ✅ Shows "Market Status Check" output
3. ✅ No errors about missing paths or modules
4. ✅ Account balance displayed (no trades with --check-only)

### Common Issues:
- **No output**: Check path is absolute, not relative
- **Module not found**: Virtual environment not activated
- **Permission denied**: Make sure user owns the directories
- **OpenD connection failed**: OpenD not running

### Set Production Schedule
Once test passes, update cron with real schedule (3:45 PM ET):
```bash
crontab -e
# Add production job without --check-only flag
45 15 * * 1-5 cd /home/youruser/spx-straddle-bot && source venv/bin/activate && python src/production_strategy_complete.py >> logs/production.log 2>&1
```

## Important Notes

- The bot checks market hours internally - won't trade if market is closed
- Holidays are handled automatically via built-in calendar
- Always monitor first few scheduled runs
- Consider network/OpenD failures in your monitoring
- Keep logs for audit trail