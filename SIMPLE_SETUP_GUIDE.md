# 🚀 Simple Setup Guide - SPX Trading Bot

This guide is for people who aren't familiar with coding. Follow each step carefully!

## What This Bot Does

This bot automatically buys SPX options (calls and puts) near market close. It's like placing a bet that the market will move significantly in either direction before the day ends.

📖 **Want to understand more?** See [How It Works](docs/HOW_IT_WORKS.md) for visual explanations!

⚠️ **WARNING**: This bot trades with REAL MONEY. Start with paper trading first!

---

## 📋 Before You Start - What You Need

1. **A Moomoo account** with options trading enabled
2. **A computer** (Mac or Windows)
3. **About 30 minutes** for setup
4. **Your Moomoo login info** including:
   - Account number
   - Password
   - Trade password (different from login password)

---

## 🛠️ Step-by-Step Setup

### Step 1: Download the Bot

1. Go to: https://github.com/kdvalentine/spx-straddle-bot
2. Click the green "Code" button
3. Click "Download ZIP"
4. Find the downloaded file (usually in Downloads folder)
5. Double-click to unzip it
6. Move the folder to your Desktop for easy access

### Step 2: Install Python (Skip if you have it)

**For Mac:**
1. Open Terminal (press Cmd+Space, type "Terminal", press Enter)
2. Copy and paste this command:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Press Enter and follow prompts
4. When done, type: `brew install python3`

**For Windows:**
1. Go to: https://www.python.org/downloads/
2. Click "Download Python" (big yellow button)
3. Run the installer
4. ⚠️ **IMPORTANT**: Check "Add Python to PATH" box
5. Click "Install Now"

### Step 3: Install Moomoo OpenD

1. Go to: https://www.moomoo.com/download/OpenAPI
2. Download OpenD for your system (Mac/Windows)
3. Install it like any other program
4. Open OpenD when done
5. Log into your Moomoo account in OpenD
6. Keep OpenD running (minimize it)

### Step 4: Open Terminal/Command Prompt

**Mac:**
- Press Cmd+Space, type "Terminal", press Enter

**Windows:**
- Press Windows key, type "cmd", press Enter

### Step 5: Navigate to Bot Folder

Type this command (replace "YourUsername" with your actual username):

**Mac:**
```
cd /Users/YourUsername/Desktop/spx-straddle-bot
```

**Windows:**
```
cd C:\Users\YourUsername\Desktop\spx-straddle-bot
```

Press Enter. If it says "no such file", check where you put the folder.

### Step 6: Run Quick Setup

**Mac:**
```
./quickstart.sh
```

**Windows:**
```
quickstart.bat
```

This will:
- Set up Python environment
- Install required packages
- Find your account numbers
- Help you configure settings

Follow the prompts - it will guide you!

### Step 7: Configure Your Settings

When prompted to edit .env file:

1. The file will open in a text editor
2. Replace these values with your info:
   ```
   MOOMOO_LOGIN_ACCOUNT=12345678        ← Your account number
   MOOMOO_LOGIN_PWD=YourPassword        ← Your login password
   MOOMOO_TRADE_PWD=YourTradePassword   ← Your trade password
   MOOMOO_ACCOUNT_ID=1234567890123      ← Will be shown by setup script
   TRADING_ENV=PAPER                    ← Keep as PAPER for testing!
   ```
3. Save the file (Ctrl+S or Cmd+S)
4. Close the editor

---

## 🏃 Running the Bot

### Test Mode (No Real Money)

Always test first! In Terminal/Command Prompt:

```
python src/production_strategy_complete.py --check-only
```

This shows:
- ✅ Connection working
- 💰 Account balance
- 📈 Current SPX price
- 🕐 Market status

### Paper Trading (Fake Money)

Practice with fake money:

```
python src/production_strategy_complete.py --paper
```

### Real Trading (Real Money!)

⚠️ **DANGER**: This uses real money!

1. Change `TRADING_ENV=REAL` in .env file
2. Run:
   ```
   python src/production_strategy_complete.py
   ```

---

## ⏰ Scheduling (Run Automatically)

### Best Time to Run
- **3:45 PM Eastern Time** (45 minutes before market close)
- Monday through Friday only

### Mac - Automatic Scheduling

1. Open Terminal
2. Type: `crontab -e`
3. Press `i` to edit
4. Add this line (replace YourUsername):
   ```
   45 15 * * 1-5 cd /Users/YourUsername/Desktop/spx-straddle-bot && source venv/bin/activate && python src/production_strategy_complete.py
   ```
5. Press Escape, type `:wq`, press Enter

### Windows - Task Scheduler

1. Create a file called `run_bot.bat` on Desktop:
   ```
   cd C:\Users\YourUsername\Desktop\spx-straddle-bot
   call venv\Scripts\activate
   python src\production_strategy_complete.py
   ```
2. Open Task Scheduler
3. Create Basic Task
4. Set to run daily at 3:45 PM
5. Choose "Start a program"
6. Browse to your `run_bot.bat` file

---

## 📊 Understanding the Output

When the bot runs, you'll see:

```
2025-01-15 15:45:00 - INFO - === Market Status Check ===
2025-01-15 15:45:00 - INFO - Market is OPEN
2025-01-15 15:45:01 - INFO - SPX Price: $6,362.90
2025-01-15 15:45:02 - INFO - Account Balance: $41,104.43
2025-01-15 15:45:03 - INFO - Buying 1 contract of SPXW240115C06350
2025-01-15 15:45:04 - INFO - Buying 1 contract of SPXW240115P06350
2025-01-15 15:45:05 - INFO - Trade complete! Total cost: $4,325.00
```

---

## 🚨 Troubleshooting

### "Cannot connect to OpenD"
- Make sure OpenD is running
- Check you're logged in to OpenD

### "No module named..."
- Run: `pip install -r requirements.txt`

### "Account not found"
- Check your account ID is correct
- Make sure trade password is right

### "Market is closed"
- Bot only trades during market hours
- Check it's not a holiday

---

## 💡 Important Tips

1. **Start Small**: Use paper trading for at least 1 week
2. **Monitor First Trades**: Watch the bot closely first few times
3. **Check Logs**: Look in `logs` folder for details
4. **Keep OpenD Running**: Must be open for bot to work
5. **Have Enough Money**: Each trade needs $3,000-8,000

---

## 🆘 Getting Help

1. **Check the logs** in the `logs` folder
2. **Read error messages** carefully
3. **Make sure OpenD is running**
4. **Verify your passwords** are correct

---

## ⚠️ Risk Warning

**OPTIONS TRADING IS RISKY!** You can lose your entire investment. This bot:
- Buys options that expire THE SAME DAY
- Can lose 100% of money spent
- Is NOT guaranteed to make profit
- Should be monitored regularly

Start with paper trading and only use money you can afford to lose!

---

## 🎯 Quick Command Reference

| What you want to do | Command to type |
|-------------------|----------------|
| Test connection | `python src/production_strategy_complete.py --check-only` |
| Paper trade | `python src/production_strategy_complete.py --paper` |
| Real trade | `python src/production_strategy_complete.py` |
| See your accounts | `python scripts/get_account_info.py` |

Remember: Always have OpenD running first!