# Twitter Retweet Bot

This is a Twitter (X) retweet bot designed to run on Termux. It uses Selenium for browser automation and Firefox as the browser.

## Features
- Retweet tweets based on a keyword search.
- Save and reuse cookies for automatic login.
- Avoid retweeting the same tweet multiple times.
- Run continuously with real-time statistics.

## Installation

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
   Ensure Firefox is installed on your device. For Geckodriver, you can install it via Termux:
   ```bash
   pkg install firefox
   ```
   Or download it manually and place it in `/data/data/com.termux/files/usr/bin/`.

3. **Set Up Cookies**
   Run the bot for the first time to set up cookies:
   ```bash
   python bothome.py
   ```
   Follow the prompts to log in and save your cookies.
      OR 
   You can export your own cookies from your own browser.
   - Copy auth_token & ct0 from your already login on X.
   - Paste to "cookies_raw.txt".
   - run "convert_cookies.py". to convert your cookies.

4. **Run the Bot**
   After setting up cookies, you can run the bot again:
   ```bash
   python bothome.py
   ```
   Enter the keyword you want to search for, and the bot will start retweeting relevant tweets.

## Usage
- The bot will continuously search for tweets containing the specified keyword.
- It will skip tweets that have already been retweeted.
- Press `Ctrl+C` to stop the bot.

## Files
- `bothome.py`: Bot script for explore the homepage retweeting requirement spesific words({self.keyword}).
- `botsearchtop.py`: Bot script for searching ({self.keyword}) top tweets.
- `botsearchlatest.py`: Bot script for searching ({self.keyword}) latest tweets.
- `requirements.txt`: List of dependencies.
- `twitter_cookies.pkl`: Saved cookies for automatic login.
- `retweeted_ids.json`: List of retweeted tweet IDs.

## Notes
- Ensure you have a stable internet connection while running the bot.
- The bot is designed for educational purposes. Use it responsibly and in compliance with Twitter's terms of service.