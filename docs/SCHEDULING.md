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
```bash
# Run SPX straddle bot at 3:45 PM ET every weekday
45 15 * * 1-5 cd /path/to/spx-straddle-bot && /path/to/spx-straddle-bot/venv/bin/python src/production_strategy_complete.py >> logs/cron.log 2>&1
```

### 3. Important considerations
- Use full paths (not ~)
- Ensure OpenD is running before scheduled time
- Check timezone settings: `timedatectl` (Linux) or `date` (macOS)
- The bot handles market hours/holidays internally

### Example with environment activation
```bash
45 15 * * 1-5 cd /home/user/spx-straddle-bot && source venv/bin/activate && python src/production_strategy_complete.py >> logs/cron.log 2>&1
```

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

1. Set a test schedule 5 minutes in the future
2. Use --check-only flag for testing
3. Verify logs are created
4. Check account wasn't charged (for --check-only)
5. Set production schedule

## Important Notes

- The bot checks market hours internally - won't trade if market is closed
- Holidays are handled automatically via built-in calendar
- Always monitor first few scheduled runs
- Consider network/OpenD failures in your monitoring
- Keep logs for audit trail