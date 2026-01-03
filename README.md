# Twitter Retweet Bot - 3-in-1 Unified Script

This is a Twitter (X) retweet bot designed to run on Termux. It uses Selenium for browser automation and Firefox as the browser. **Now with 3 modes in a single script!**

## ✨ Features
- **3 Modes in 1 Script**: Home Timeline, Search Top, or Search Latest
- Retweet tweets based on keyword search or filter
- Save and reuse cookies for automatic login
- Real-time scroll counter and tweet ID notifications
- Anti-click error with JavaScript fallback
- No permanent tracking files (privacy-focused)
- Run continuously with live status updates

## 🎯 3 Available Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Mode 1** | Home Timeline with keyword filter | Retweet from your timeline containing specific words |
| **Mode 2** | Search Top | Retweet most popular/engaging tweets with keyword |
| **Mode 3** | Search Latest | Retweet newest tweets with keyword (real-time) |

## 📋 Installation

### Prerequisites
- Termux (for Android)
- Python 3.8 or higher
- Firefox browser
- Geckodriver

### Steps

1. **Install Python and Dependencies**
   Open Termux and run the following commands:
   ```bash
   pkg update && pkg upgrade
   pkg install python
   pip install -r requirements.txt
   ```

2. **Install Firefox and Geckodriver**
   Ensure Firefox is installed on your device. For Geckodriver, install it via Termux:
   ```bash
   pkg install firefox
   ```
   Or download it manually and place it in `/data/data/com.termux/files/usr/bin/`.

3. **Set Up Cookies**
   
   **Option A: Automatic Setup (Recommended)**
   Run the bot for the first time to set up cookies automatically:
   ```bash
   python bot.py
   ```
   Follow the prompts to log in and save your cookies.
   
   **Option B: Manual Cookie Export**
   You can export your own cookies from your browser:
   - Copy `auth_token` & `ct0` from your already logged-in X session
   - Paste to `cookies_raw.txt`
   - Run the converter:
   ```bash
   python convert_cookies.py
   ```
   - Bot is now ready to use the converted cookies for auto login

4. **Run the Bot**
   After setting up cookies, run the unified bot:
   ```bash
   python bot.py
   ```
   - Select your preferred mode (1/2/3)
   - Enter the keyword
   - The bot will start retweeting relevant tweets

## 🚀 Usage

### Running the Bot
```bash
python bot.py
```

**Interactive Menu:**
```
🎯 PILIH MODE:
1. Home Timeline (dengan filter keyword)
2. Search Top (hasil teratas)
3. Search Latest (terbaru)

Pilih mode (1/2/3): 2
Keyword pencarian: bitcoin
```

### What You'll See
```
✓ Berhasil retweet: 1234567890123456789
⊘ Skip (sudah di-retweet): 9876543210987654321
🔄 Scroll ke-1
🔄 Scroll ke-2
```

### Controls
- The bot will continuously search/monitor for tweets
- It will skip tweets that have already been retweeted in the current session
- Press `Ctrl+C` to stop the bot safely

## 📁 Files

### Main Files
- **`bot.py`**: 🆕 Unified bot script with 3 modes (RECOMMENDED)
- `convert_cookies.py`: Convert `cookies_raw.txt` to `twitter_cookies.pkl`
- `requirements.txt`: List of dependencies
- `twitter_cookies.pkl`: Saved cookies for automatic login

### Legacy Files (Optional)
- `bothome.py`: Standalone bot for home timeline mode
- `botsearchtop.py`: Standalone bot for search top mode
- `botsearchlatest.py`: Standalone bot for search latest mode

> **Note**: The unified `bot.py` includes all features from the legacy files. Use the individual files only if you need a specific single-mode bot.

## 🔧 Technical Details

### Cookie-Based Authentication
- First run: Setup cookies via automatic login
- Subsequent runs: Auto-login using saved cookies
- No need to enter credentials repeatedly

### Anti-Detection Features
- Smooth scrolling that mimics human behavior
- Random delays between actions
- Mobile user agent spoofing
- Headless Firefox browser operation
- JavaScript click fallback for blocked elements

### Privacy & Tracking
- **No permanent tracking**: Bot doesn't save `retweeted_ids.json`
- Session-only detection: Checks unretweet button status
- Lightweight and privacy-focused

## ⚙️ Mode Details

### Mode 1: Home Timeline
- Monitors your home feed
- Filters tweets containing your specified keyword
- Best for: Engaging with your network's content

### Mode 2: Search Top
- Searches for keyword across all of X
- Shows most popular/engaging results first
- Best for: High-quality, viral content

### Mode 3: Search Latest
- Searches for keyword across all of X
- Shows newest tweets first (real-time)
- Best for: Breaking news, trending topics, immediate engagement

## 📝 Notes

- Ensure you have a stable internet connection while running the bot
- The bot is designed for educational purposes
- **Use responsibly and in compliance with X's (Twitter) terms of service**
- Automated actions may result in account restrictions or bans
- Consider rate limits and avoid excessive retweeting

## ⚠️ Disclaimer

This bot is for educational and research purposes only. Automated interactions with social media platforms may violate their terms of service. Users are responsible for ensuring their use complies with all applicable laws and platform policies. The developers assume no liability for misuse or any consequences resulting from the use of this software.

## 🆘 Troubleshooting

### "Cookies expired or invalid"
- Re-run the setup: Delete `twitter_cookies.pkl` and run `python bot.py` again
- Or manually export fresh cookies using Option B

### "Element not clickable" errors
- Already fixed with JavaScript fallback in the latest version
- Ensure you're using the updated `bot.py`

### Bot not finding tweets
- Check your internet connection
- Verify the keyword is correct
- Try a different mode (some keywords work better in search modes)

## 📜 License

MIT License - Feel free to modify and distribute

---

**Happy Retweeting! 🐦✨**
