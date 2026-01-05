# Twitter Retweet Bot - 3-in-1 Unified Script

This is a Twitter (X) retweet bot designed to run on Termux. It uses Selenium for browser automation and Firefox as the browser. **Now with 3 modes in a single script!**

## ✨ Features
- **3 Modes in 1 Script**: Home Timeline, Search Top, or Search Latest
- **Multi-Cookie Support**: Use multiple accounts with different cookie files
- **🆕 Auto-Refresh**: Automatically refresh when no tweets found (Mode 1)
- **🆕 Logout Detection**: Detects when X logs you out or flags account
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

## 🆕 New Features in v2.0

### Auto-Refresh (Mode 1)
- Automatically refreshes the page after **5 consecutive scrolls** without finding matching tweets
- Prevents infinite scrolling when timeline has no new content
- Progress indicator: `📊 Scroll tanpa tweet cocok: 3/5`
- Counter resets when a matching tweet is found

### Logout Detection 🛡️
The bot now detects various logout scenarios:
- ✅ Session expiration
- ✅ X/Twitter spam detection
- ✅ Account verification challenges
- ✅ Suspicious activity warnings
- ✅ Forced re-authentication

When logout is detected:
- Bot automatically stops
- Saves screenshot for debugging
- Shows informative error message with solutions
- Suggests next steps to recover

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

### Running the Bot with Multi-Cookie Support

The bot now supports multiple cookie files for using different accounts with **flexible naming**:

```bash
python bot.py
```

When you run the bot, it will:
1. Show a list of ALL available `.pkl` cookie files (e.g., `twitter_cookies.pkl`, `akun_kerja.pkl`, `cookies1.pkl`, etc.)
2. Let you select which account to use
3. Continue with the selected mode and keyword

### Creating Multiple Cookie Files with Flexible Naming

To create additional cookie files with custom names:

1. Prepare your cookies in `cookies_raw.txt`
2. Run the converter:
```bash
python convert_cookies.py
```
3. **Type any custom name** you want (e.g., `akun_kerja`, `personal_account`, `client_x`)
4. The converter will automatically add `.pkl` extension
5. Repeat for each account with different names

**Examples of valid cookie names:**
- `twitter_cookies.pkl` (default)
- `cookies1.pkl`, `cookies2.pkl` (numbered)
- `akun_kerja.pkl` (Indonesian naming)
- `personal_account.pkl` (descriptive)
- `client-x-project.pkl` (with hyphens)

### Running the Bot

**Interactive Menu:**
```
🎯 SELECT MODE:
1. Home Timeline (with keyword filter)
2. Search Top (top results)
3. Search Latest (latest tweets)

Select mode (1/2/3): 1
Keyword to filter in Home Timeline: giveaway
```

### What You'll See

**Normal Operation:**
```
✓ Successfully retweeted: 1234567890123456789
⊘ Skip (already retweeted): 9876543210987654321
🔄 Scroll #1
📊 Scrolls without matching tweets: 2/5
```

**Auto-Refresh (Mode 1):**
```
📊 Scrolls without matching tweets: 5/5
🔄 REFRESH PAGE - Resetting tweet search...
✓ Page refreshed, starting new search
```

**Logout Detection:**
```
⚠️  LOGOUT DETECTED!
Possible causes:
1. X detected suspicious/spam activity
2. Session cookies expired
3. Account logged out from another device

Solutions:
1. Try logging in again from normal browser
2. Wait a few hours before trying again
3. Use another account or create new cookies
📸 Screenshot saved: logout_screenshot_1735123456.png
```

### Controls
- The bot will continuously search/monitor for tweets
- It will skip tweets that have already been retweeted in the current session
- **Mode 1 only**: Auto-refreshes after 5 scrolls without matching tweets
- Press `Ctrl+C` to stop the bot safely

## 📁 Files

### Main Files
- **`bot.py`**: 🆕 Unified bot script v2.0 with auto-refresh & logout detection (RECOMMENDED)
- `convert_cookies.py`: Convert `cookies_raw.txt` to multiple cookie files
- `requirements.txt`: List of dependencies
- `twitter_cookies.pkl`: Default saved cookies for automatic login
- `cookies1.pkl`, `cookies2.pkl`, etc.: Additional cookie files for multiple accounts
- `logout_screenshot_*.png`: Debug screenshots when logout is detected

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
- 🆕 Smart logout detection to avoid wasted sessions

### Auto-Refresh Logic (Mode 1)
```
No matching tweets found → Scroll (1/5)
Still no matches → Scroll (2/5)
...
Still no matches → Scroll (5/5)
→ Auto-refresh page and reset counter
→ Continue searching from fresh timeline
```

### Logout Detection Algorithm
The bot checks for multiple indicators:
1. **URL Redirects**: `/i/flow/login`, `/login`, `/account/access`
2. **Login Forms**: Presence of username and password input fields
3. **Challenge Screens**: "Verify your identity", "automated behavior"
4. **Navigation Loss**: Missing sidebar navigation elements
5. **Session Checks**: Performed every iteration to catch early

### Privacy & Tracking
- **No permanent tracking**: Bot doesn't save `retweeted_ids.json`
- Session-only detection: Checks unretweet button status
- Lightweight and privacy-focused

## ⚙️ Mode Details

### Mode 1: Home Timeline
- Monitors your home feed
- Filters tweets containing your specified keyword (case-insensitive)
- **Auto-refresh feature enabled** (5 scroll limit)
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
- 🆕 Monitor logout screenshots if account gets flagged
- 🆕 Use multiple cookies to rotate accounts if one gets restricted

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
- **Mode 1**: Wait for auto-refresh after 5 scrolls

### Bot says "LOGOUT DETECTED"
**This is a real logout/restriction from X. Solutions:**

1. **Check the screenshot**: Look at `logout_screenshot_*.png` to see what X is showing
2. **If spam detection**:
   - Wait 6-24 hours before trying again
   - Reduce retweet frequency (add longer delays in code)
   - Use different account temporarily
3. **If session expired**:
   - Delete old cookie file
   - Run `python bot.py` to create new cookies
4. **If account locked**:
   - Log in via browser to complete verification
   - Export new cookies after verification
5. **Prevention tips**:
   - Don't run bot 24/7
   - Use realistic delays (3-10 seconds between retweets)
   - Avoid retweeting too many posts per hour
   - Mix manual activity with bot activity

### Bot keeps refreshing (Mode 1)
- This is normal if your timeline has no tweets matching the keyword
- Check if your keyword is too specific
- Try using partial words or more common terms
- Ensure you're following accounts that post about your keyword

### False logout detection
- Very rare with v2.0 improvements
- Check your internet connection
- Manually verify you're still logged in via browser
- Report issue if it persists

## 🔄 Changelog

### v2.0 (Latest)
- ✨ Added auto-refresh feature for Mode 1 (5 scroll limit)
- 🛡️ Improved logout detection algorithm
- 📸 Automatic screenshot on logout for debugging
- 🔧 More accurate session validation
- 📊 Real-time counter display for refresh trigger
- 🐛 Fixed false positive logout detections
- ⚡ Better error handling and recovery

### v1.0
- Initial release with 3 modes
- Multi-cookie support
- Basic authentication system

## 📜 License

MIT License - Feel free to modify and distribute

---

**Happy Retweeting! 🐦✨**
