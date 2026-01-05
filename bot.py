#!/usr/bin/env python3
"""
Bot Retweet X (Twitter) untuk Termux - 3 Mode dalam 1 Script
Mode 1: Home Timeline
Mode 2: Search Top
Mode 3: Search Latest

Fitur Tambahan:
- Auto refresh jika tidak menemukan tweet setelah 5x scroll (Mode 1)
- Deteksi logout otomatis
"""

import time
import os
import pickle
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TwitterRetweetBot:
    def __init__(self, keyword, mode, cookies_file='twitter_cookies.pkl'):
        self.keyword = keyword
        self.mode = mode  # 1=home, 2=search_top, 3=search_latest
        self.cookies_file = cookies_file
        self.driver = None
        self.scroll_count = 0
        self.available_cookies = []
        self.no_tweet_scroll_count = 0  # Counter untuk scroll tanpa tweet
        self.max_no_tweet_scrolls = 5   # Max scroll sebelum refresh
        
        # Untuk mode home, keyword filter diperlukan
        if mode == 1:
            self.required_keyword = self.keyword
    
    def find_available_cookies(self):
        """Find all available cookie files"""
        cookie_files = glob.glob('*.pkl')
        
        if 'twitter_cookies.pkl' in cookie_files:
            cookie_files.remove('twitter_cookies.pkl')
            cookie_files.insert(0, 'twitter_cookies.pkl')
        
        return cookie_files
    
    def select_cookie_file(self):
        """Select cookie file from available list"""
        self.available_cookies = self.find_available_cookies()
        
        if not self.available_cookies:
            print("❌ No cookie files found!")
            return None
        
        print("\n📁 SELECT COOKIE FILE:")
        for i, cookie_file in enumerate(self.available_cookies):
            print(f"{i+1}. {cookie_file}")
        
        while True:
            try:
                choice = int(input(f"\nSelect cookie (1-{len(self.available_cookies)}): "))
                if 1 <= choice <= len(self.available_cookies):
                    selected_cookie = self.available_cookies[choice-1]
                    print(f"✓ Cookie selected: {selected_cookie}")
                    return selected_cookie
                else:
                    print(f"❌ Choose between 1 to {len(self.available_cookies)}!")
            except ValueError:
                print(f"❌ Enter a number between 1 to {len(self.available_cookies)}!")
    
    def is_logged_out(self):
        """Deteksi apakah akun telah logout"""
        try:
            current_url = self.driver.current_url
            
            # Indikator PASTI logout - URL redirect ke login
            logout_urls = [
                "/i/flow/login",
                "/login", 
                "/account/access"
            ]
            
            for logout_url in logout_urls:
                if logout_url in current_url and "home" not in current_url:
                    return True
            
            # Cek elemen yang HANYA muncul saat logout (bukan di feed)
            # Gunakan kombinasi selector yang lebih spesifik
            try:
                # Cek apakah ada form login
                login_form = self.driver.find_elements(By.CSS_SELECTOR, 'input[name="text"][autocomplete="username"]')
                password_form = self.driver.find_elements(By.CSS_SELECTOR, 'input[name="password"]')
                
                if login_form and password_form:
                    return True
            except:
                pass
            
            # Cek pesan challenge/verifikasi yang memaksa re-login
            challenge_indicators = [
                '//span[contains(text(), "Verify your identity")]',
                '//span[contains(text(), "Enter your password")]',
                '//span[contains(text(), "Confirm your email")]',
                '//span[contains(text(), "Confirm your phone")]',
                '//h1[contains(text(), "Help us keep your account safe")]',
                '//span[contains(text(), "automated behavior")]',
                '//span[contains(text(), "We detected unusual")]'
            ]
            
            for indicator in challenge_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements and elements[0].is_displayed():
                        # Double check - pastikan bukan di homepage
                        if "home" not in current_url:
                            return True
                except:
                    continue
            
            # Cek apakah sidebar/navigation hilang (tanda session lost)
            try:
                nav_home = self.driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="AppTabBar_Home_Link"]')
                if not nav_home:
                    # Navigation hilang, kemungkinan logout
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error saat cek logout: {e}")
            return False
    
    def handle_logout(self):
        """Handle if logout is detected"""
        print("\n" + "="*50)
        print("⚠️  LOGOUT DETECTED!")
        print("="*50)
        print("Possible causes:")
        print("1. X detected suspicious/spam activity")
        print("2. Session cookies expired")
        print("3. Account logged out from another device")
        print("\nSolutions:")
        print("1. Try logging in again from normal browser")
        print("2. Wait a few hours before trying again")
        print("3. Use another account or create new cookies")
        print("="*50 + "\n")
        
        # Save screenshot for debugging
        try:
            screenshot_name = f"logout_screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_name)
            print(f"📸 Screenshot saved: {screenshot_name}")
        except:
            pass
    
    def setup_driver(self):
        """Setup Firefox driver untuk Termux"""
        print("Setting up Firefox driver...")
        
        from selenium.webdriver.firefox.service import Service
        
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('general.useragent.override', 
                              'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/115.0')
        
        service = Service('/data/data/com.termux/files/usr/bin/geckodriver')
        
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.set_page_load_timeout(30)
        print("✓ Firefox driver ready!")
        
    def save_cookies(self):
        """Simpan cookies setelah login manual"""
        with open(self.cookies_file, 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)
        print(f"✓ Cookies disimpan ke {self.cookies_file}")
    
    def load_cookies(self):
        """Load cookies yang sudah disimpan"""
        if not os.path.exists(self.cookies_file):
            return False
        
        try:
            self.driver.get("https://x.com")
            time.sleep(2)
            
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            print("✓ Cookies berhasil dimuat")
            return True
        except Exception as e:
            print(f"✗ Gagal load cookies: {e}")
            return False
    
    def manual_login_for_cookies(self, username, password):
        """Manual login to get cookies (only once)"""
        print("\n=== SETUP COOKIES (ONLY ONCE) ===")
        print("Bot will login to save cookies...")
        
        self.driver.get("https://x.com/i/flow/login")
        time.sleep(2)
        
        try:
            print("Entering username...")
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.send_keys(username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(3)
            
            print("Entering password...")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            print("Waiting for login to complete...")
            time.sleep(10)
            
            self.save_cookies()
            print("✓ Login successful and cookies saved!")
            print("Next time bot will use these cookies (no need to login again)\n")
            return True
            
        except Exception as e:
            print(f"✗ Manual login failed: {e}")
            print("\nALTERNATIVE: Login manually in browser, then export cookies")
            return False
    
    def login(self):
        """Login using cookies"""
        print("Logging in using cookies...")
        
        if self.load_cookies():
            self.driver.refresh()
            time.sleep(3)
            
            self.driver.get("https://x.com/home")
            time.sleep(3)
            
            if "home" in self.driver.current_url:
                print("✓ Login successful with cookies!")
                return True
            else:
                print("✗ Cookies expired or invalid")
                return False
        else:
            print("✗ Cookies not found")
            return False
    
    def navigate_to_target(self):
        """Navigasi ke halaman target berdasarkan mode"""
        from urllib.parse import quote
        
        if self.mode == 1:
            url = "https://x.com/home/"
            print(f"Mode: Home Timeline (Filter keyword: {self.keyword})")
        elif self.mode == 2:
            encoded_keyword = quote(self.keyword)
            url = f"https://x.com/search?q={encoded_keyword}&src=typed_query"
            print(f"Mode: Search Top (Keyword: {self.keyword})")
        elif self.mode == 3:
            encoded_keyword = quote(self.keyword)
            url = f"https://x.com/search?q={encoded_keyword}&src=typed_query&f=live"
            print(f"Mode: Search Latest (Keyword: {self.keyword})")
        
        self.driver.get(url)
        time.sleep(3)
    
    def refresh_page(self):
        """Refresh page and reset counter"""
        print("\n🔄 REFRESH PAGE - Resetting tweet search...")
        self.driver.refresh()
        time.sleep(3)
        self.no_tweet_scroll_count = 0
        print("✓ Page refreshed, starting new search\n")
    
    def get_tweet_id(self, tweet_element):
        """Dapatkan ID unik dari tweet"""
        try:
            link = tweet_element.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
            href = link.get_attribute('href')
            tweet_id = href.split('/status/')[-1].split('?')[0]
            return tweet_id
        except:
            return None
    
    def check_required_keyword(self, tweet_element):
        """Cek apakah tweet mengandung keyword yang diperlukan (hanya untuk mode home)"""
        if self.mode != 1:
            return True
        
        if not hasattr(self, 'required_keyword'):
            return True
        
        try:
            tweet_text = tweet_element.text.lower()
            keyword_lower = self.required_keyword.lower()
            if keyword_lower in tweet_text:
                return True
            else:
                return False
        except:
            return False
    
    def wait_for_tweets_load(self, timeout=10):
        """Wait until tweets appear"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            tweets = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            if len(tweets) > 0:
                return True
            time.sleep(1)
        return False

    def is_already_retweeted(self, tweet_element):
        """Check if tweet is already retweeted"""
        try:
            tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="unretweet"]')
            return True
        except NoSuchElementException:
            return False
    
    def retweet_tweet(self, tweet_element, tweet_id):
        """Retweet a tweet"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet_element)
            time.sleep(0.5)
            
            retweet_btn = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]')
            
            try:
                retweet_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", retweet_btn)
            
            time.sleep(1)
            
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))
            )
            
            try:
                confirm_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", confirm_btn)
            
            time.sleep(2)
            
            print(f"✓ Successfully retweeted: {tweet_id}")
            return True
        except Exception as e:
            print(f"✗ Failed to retweet: {e}")
            return False
    
    def scroll_page(self):
        """Scroll halaman untuk load tweet baru"""
        if self.mode == 1:
            self.driver.execute_script("""
                let scrollAmount = 500;
                let scrollStep = 15;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount -= scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(1.5)

            self.driver.execute_script("""
                let scrollAmount = 200;
                let scrollStep = -10;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount += scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(0.8)

            self.driver.execute_script("""
                let scrollAmount = 700;
                let scrollStep = 15;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount -= scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(2.5)
        else:
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
                
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(1)
            self.driver.execute_script("window.scrollBy(0, 700);")
            
    def run(self):
        """Run bot continuously"""
        try:
            self.setup_driver()
            
            if not self.login():
                print("\n❌ Bot stopped due to login failure")
                print("Run: python bot.py or transfer cookies from browser for self login")
                return
            
            self.navigate_to_target()
            
            print("\n=== Bot started running ===")
            if self.mode == 1 and hasattr(self, 'required_keyword'):
                print(f"🔍 Filter active: only retweet containing '{self.required_keyword}'")
                print(f"⚡ Auto-refresh: after {self.max_no_tweet_scrolls}x scroll without tweets")
            print("🛡️ Logout detection: ACTIVE")
            print("Press Ctrl+C to stop\n")
            
            while True:
                # Check logout on every iteration
                if self.is_logged_out():
                    self.handle_logout()
                    break
                
                # Wait for tweets to load (for search modes)
                if self.mode in [2, 3]:
                    if not self.wait_for_tweets_load():
                        print("⏱️ Timeout waiting for tweets, scrolling...")
                        self.scroll_page()
                        continue
                
                # Get all tweets on page
                tweets = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                if not tweets:
                    print("⚠️ No tweets found, scrolling...")
                    self.scroll_page()
                    
                    # Increment counter for mode 1
                    if self.mode == 1:
                        self.no_tweet_scroll_count += 1
                        print(f"📊 Scrolls without tweets: {self.no_tweet_scroll_count}/{self.max_no_tweet_scrolls}")
                        
                        # Refresh if limit reached
                        if self.no_tweet_scroll_count >= self.max_no_tweet_scrolls:
                            self.refresh_page()
                    
                    continue
                
                # Tweets found
                found_matching_tweet = False
                
                for tweet in tweets:
                    try:
                        tweet_id = self.get_tweet_id(tweet)
                        
                        if not tweet_id:
                            continue
                        
                        # Check if already retweeted
                        if self.is_already_retweeted(tweet):
                            print(f"⊘ Skip (already retweeted): {tweet_id}")
                            continue
                        
                        # Check required keyword (only for home mode)
                        if not self.check_required_keyword(tweet):
                            continue
                        
                        # Tweet matches filter, reset counter
                        found_matching_tweet = True
                        if self.mode == 1:
                            self.no_tweet_scroll_count = 0
                        
                        # Retweet tweet
                        self.retweet_tweet(tweet, tweet_id)
                        time.sleep(3)
                        
                    except Exception as e:
                        continue
                
                # If mode 1 and no matching tweets after scroll
                if self.mode == 1 and not found_matching_tweet:
                    self.no_tweet_scroll_count += 1
                    print(f"📊 Scrolls without matching tweets: {self.no_tweet_scroll_count}/{self.max_no_tweet_scrolls}")
                    
                    if self.no_tweet_scroll_count >= self.max_no_tweet_scrolls:
                        self.refresh_page()
                
                # Scroll to find new tweets
                self.scroll_count += 1
                print(f"🔄 Scroll #{self.scroll_count}\n")
                self.scroll_page()
                time.sleep(8)
                
        except KeyboardInterrupt:
            print("\n\n✓ Bot stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    print("="*50)
    print("TWITTER/X RETWEET BOT - 3-IN-1")
    print("v2.0 - Auto Refresh & Logout Detection")
    print("="*50)
    
    # Check if cookies are available
    bot = TwitterRetweetBot("", 1)
    available_cookies = bot.find_available_cookies()
    
    if not available_cookies:
        print("\n⚠️  NO COOKIES FOUND!")
        print("Bot will setup cookies first...\n")
         
        username = input("X Username/Email: ")
        password = input("X Password: ")
         
        # Dummy bot for cookie setup
        bot.setup_driver()
        if bot.manual_login_for_cookies(username, password):
            print("\n✓ Setup complete! Please run the bot again.\n")
        else:
            print("\n✗ Setup failed. Please try again.\n")
        exit()
    
    # Select cookie file
    selected_cookie = bot.select_cookie_file()
    if not selected_cookie:
        exit()
    
    # Mode selection menu
    print("\n🎯 SELECT MODE:")
    print("1. Home Timeline (with keyword filter)")
    print("2. Search Top (top results)")
    print("3. Search Latest (latest tweets)")
    
    while True:
        try:
            mode = int(input("\nSelect mode (1/2/3): "))
            if mode in [1, 2, 3]:
                break
            else:
                print("❌ Choose between 1, 2, or 3!")
        except ValueError:
            print("❌ Enter a number 1, 2, or 3!")
    
    # Keyword input
    if mode == 1:
        KEYWORD = input("Keyword to filter in Home Timeline: ")
    else:
        KEYWORD = input("Search keyword: ")
     
    print("\n" + "="*50)
    
    bot = TwitterRetweetBot(KEYWORD, mode, selected_cookie)
    bot.run()        print("2. Tunggu beberapa jam sebelum mencoba lagi")
        print("3. Gunakan akun lain atau buat cookie baru")
        print("="*50 + "\n")
        
        # Simpan screenshot untuk debugging
        try:
            screenshot_name = f"logout_screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_name)
            print(f"📸 Screenshot disimpan: {screenshot_name}")
        except:
            pass
    
    def setup_driver(self):
        """Setup Firefox driver untuk Termux"""
        print("Setting up Firefox driver...")
        
        from selenium.webdriver.firefox.service import Service
        
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('general.useragent.override', 
                              'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/115.0')
        
        service = Service('/data/data/com.termux/files/usr/bin/geckodriver')
        
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.set_page_load_timeout(30)
        print("✓ Firefox driver ready!")
        
    def save_cookies(self):
        """Simpan cookies setelah login manual"""
        with open(self.cookies_file, 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)
        print(f"✓ Cookies disimpan ke {self.cookies_file}")
    
    def load_cookies(self):
        """Load cookies yang sudah disimpan"""
        if not os.path.exists(self.cookies_file):
            return False
        
        try:
            self.driver.get("https://x.com")
            time.sleep(2)
            
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            print("✓ Cookies berhasil dimuat")
            return True
        except Exception as e:
            print(f"✗ Gagal load cookies: {e}")
            return False
    
    def manual_login_for_cookies(self, username, password):
        """Login manual untuk ambil cookies (hanya sekali)"""
        print("\n=== SETUP COOKIES (HANYA SEKALI) ===")
        print("Bot akan login untuk mengambil cookies...")
        
        self.driver.get("https://x.com/i/flow/login")
        time.sleep(2)
        
        try:
            print("Isi username...")
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.send_keys(username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(3)
            
            print("Isi password...")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            print("Menunggu login selesai...")
            time.sleep(10)
            
            self.save_cookies()
            print("✓ Login berhasil dan cookies tersimpan!")
            print("Selanjutnya bot akan pakai cookies ini (tidak perlu login lagi)\n")
            return True
            
        except Exception as e:
            print(f"✗ Login manual gagal: {e}")
            print("\nALTERNATIF: Login manual di browser, lalu export cookies")
            return False
    
    def login(self):
        """Login menggunakan cookies"""
        print("Login menggunakan cookies...")
        
        if self.load_cookies():
            self.driver.refresh()
            time.sleep(3)
            
            self.driver.get("https://x.com/home")
            time.sleep(3)
            
            if "home" in self.driver.current_url:
                print("✓ Login berhasil dengan cookies!")
                return True
            else:
                print("✗ Cookies expired atau invalid")
                return False
        else:
            print("✗ Cookies tidak ditemukan")
            return False
    
    def navigate_to_target(self):
        """Navigasi ke halaman target berdasarkan mode"""
        from urllib.parse import quote
        
        if self.mode == 1:
            url = "https://x.com/home/"
            print(f"Mode: Home Timeline (Filter keyword: {self.keyword})")
        elif self.mode == 2:
            encoded_keyword = quote(self.keyword)
            url = f"https://x.com/search?q={encoded_keyword}&src=typed_query"
            print(f"Mode: Search Top (Keyword: {self.keyword})")
        elif self.mode == 3:
            encoded_keyword = quote(self.keyword)
            url = f"https://x.com/search?q={encoded_keyword}&src=typed_query&f=live"
            print(f"Mode: Search Latest (Keyword: {self.keyword})")
        
        self.driver.get(url)
        time.sleep(3)
    
    def refresh_page(self):
        """Refresh halaman dan reset counter"""
        print("\n🔄 REFRESH PAGE - Reset pencarian tweet...")
        self.driver.refresh()
        time.sleep(3)
        self.no_tweet_scroll_count = 0
        print("✓ Halaman di-refresh, mulai pencarian baru\n")
    
    def get_tweet_id(self, tweet_element):
        """Dapatkan ID unik dari tweet"""
        try:
            link = tweet_element.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
            href = link.get_attribute('href')
            tweet_id = href.split('/status/')[-1].split('?')[0]
            return tweet_id
        except:
            return None
    
    def check_required_keyword(self, tweet_element):
        """Cek apakah tweet mengandung keyword yang diperlukan (hanya untuk mode home)"""
        if self.mode != 1:
            return True
        
        if not hasattr(self, 'required_keyword'):
            return True
        
        try:
            tweet_text = tweet_element.text.lower()
            keyword_lower = self.required_keyword.lower()
            if keyword_lower in tweet_text:
                return True
            else:
                return False
        except:
            return False
    
    def wait_for_tweets_load(self, timeout=10):
        """Tunggu sampai tweet muncul"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            tweets = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            if len(tweets) > 0:
                return True
            time.sleep(1)
        return False

    def is_already_retweeted(self, tweet_element):
        """Cek apakah tweet sudah di-retweet"""
        try:
            tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="unretweet"]')
            return True
        except NoSuchElementException:
            return False
    
    def retweet_tweet(self, tweet_element, tweet_id):
        """Retweet sebuah tweet"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet_element)
            time.sleep(0.5)
            
            retweet_btn = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]')
            
            try:
                retweet_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", retweet_btn)
            
            time.sleep(1)
            
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))
            )
            
            try:
                confirm_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", confirm_btn)
            
            time.sleep(2)
            
            print(f"✓ Berhasil retweet: {tweet_id}")
            return True
        except Exception as e:
            print(f"✗ Gagal retweet: {e}")
            return False
    
    def scroll_page(self):
        """Scroll halaman untuk load tweet baru"""
        if self.mode == 1:
            self.driver.execute_script("""
                let scrollAmount = 500;
                let scrollStep = 15;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount -= scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(1.5)

            self.driver.execute_script("""
                let scrollAmount = 200;
                let scrollStep = -10;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount += scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(0.8)

            self.driver.execute_script("""
                let scrollAmount = 700;
                let scrollStep = 15;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount -= scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(2.5)
        else:
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
                
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(1)
            self.driver.execute_script("window.scrollBy(0, 700);")
            
    def run(self):
        """Jalankan bot secara terus-menerus"""
        try:
            self.setup_driver()
            
            if not self.login():
                print("\n❌ Bot berhenti karena gagal login")
                print("Jalankan: python bot.py atau transfer cookies dari browser untuk self login")
                return
            
            self.navigate_to_target()
            
            print("\n=== Bot mulai berjalan ===")
            if self.mode == 1 and hasattr(self, 'required_keyword'):
                print(f"🔍 Filter aktif: hanya retweet yang mengandung '{self.required_keyword}'")
                print(f"⚡ Auto-refresh: setelah {self.max_no_tweet_scrolls}x scroll tanpa tweet")
            print("🛡️ Deteksi logout: AKTIF")
            print("Tekan Ctrl+C untuk menghentikan\n")
            
            while True:
                # Cek logout di setiap iterasi
                if self.is_logged_out():
                    self.handle_logout()
                    break
                
                # Tunggu tweet load (untuk mode search)
                if self.mode in [2, 3]:
                    if not self.wait_for_tweets_load():
                        print("⏱️ Timeout waiting for tweets, scroll...")
                        self.scroll_page()
                        continue
                
                # Ambil semua tweet di halaman
                tweets = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                if not tweets:
                    print("⚠️ Tidak ada tweet ditemukan, scroll...")
                    self.scroll_page()
                    
                    # Increment counter untuk mode 1
                    if self.mode == 1:
                        self.no_tweet_scroll_count += 1
                        print(f"📊 Scroll tanpa tweet: {self.no_tweet_scroll_count}/{self.max_no_tweet_scrolls}")
                        
                        # Refresh jika sudah mencapai limit
                        if self.no_tweet_scroll_count >= self.max_no_tweet_scrolls:
                            self.refresh_page()
                    
                    continue
                
                # Ada tweet ditemukan
                found_matching_tweet = False
                
                for tweet in tweets:
                    try:
                        tweet_id = self.get_tweet_id(tweet)
                        
                        if not tweet_id:
                            continue
                        
                        # Cek apakah sudah pernah di-retweet
                        if self.is_already_retweeted(tweet):
                            print(f"⊘ Skip (sudah di-retweet): {tweet_id}")
                            continue
                        
                        # Cek keyword yang diperlukan (hanya untuk mode home)
                        if not self.check_required_keyword(tweet):
                            continue
                        
                        # Tweet cocok dengan filter, reset counter
                        found_matching_tweet = True
                        if self.mode == 1:
                            self.no_tweet_scroll_count = 0
                        
                        # Retweet tweet
                        self.retweet_tweet(tweet, tweet_id)
                        time.sleep(3)
                        
                    except Exception as e:
                        continue
                
                # Jika mode 1 dan tidak ada tweet yang cocok setelah scroll
                if self.mode == 1 and not found_matching_tweet:
                    self.no_tweet_scroll_count += 1
                    print(f"📊 Scroll tanpa tweet cocok: {self.no_tweet_scroll_count}/{self.max_no_tweet_scrolls}")
                    
                    if self.no_tweet_scroll_count >= self.max_no_tweet_scrolls:
                        self.refresh_page()
                
                # Scroll untuk mencari tweet baru
                self.scroll_count += 1
                print(f"🔄 Scroll ke-{self.scroll_count}\n")
                self.scroll_page()
                time.sleep(8)
                
        except KeyboardInterrupt:
            print("\n\n✓ Bot dihentikan oleh user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    print("="*50)
    print("BOT RETWEET X (TWITTER) - 3-IN-1")
    print("v2.0 - Auto Refresh & Logout Detection")
    print("="*50)
    
    # Cek apakah ada cookies yang tersedia
    bot = TwitterRetweetBot("", 1)
    available_cookies = bot.find_available_cookies()
    
    if not available_cookies:
        print("\n⚠️  COOKIES BELUM ADA!")
        print("Bot akan setup cookies terlebih dahulu...\n")
         
        username = input("Username/Email X: ")
        password = input("Password X: ")
         
        # Dummy bot untuk setup cookies
        bot.setup_driver()
        if bot.manual_login_for_cookies(username, password):
            print("\n✓ Setup selesai! Silakan jalankan bot lagi.\n")
        else:
            print("\n✗ Setup gagal. Silakan coba lagi.\n")
        exit()
    
    # Pilih cookie file
    selected_cookie = bot.select_cookie_file()
    if not selected_cookie:
        exit()
    
    # Menu pilihan mode
    print("\n🎯 PILIH MODE:")
    print("1. Home Timeline (dengan filter keyword)")
    print("2. Search Top (hasil teratas)")
    print("3. Search Latest (terbaru)")
    
    while True:
        try:
            mode = int(input("\nPilih mode (1/2/3): "))
            if mode in [1, 2, 3]:
                break
            else:
                print("❌ Pilih antara 1, 2, atau 3!")
        except ValueError:
            print("❌ Masukkan angka 1, 2, atau 3!")
    
    # Input keyword
    if mode == 1:
        KEYWORD = input("Keyword untuk filter di Home Timeline: ")
    else:
        KEYWORD = input("Keyword pencarian: ")
     
    print("\n" + "="*50)
    
    bot = TwitterRetweetBot(KEYWORD, mode, selected_cookie)
    bot.run()            self.save_cookies()
            print("✓ Login berhasil dan cookies tersimpan!")
            print("Selanjutnya bot akan pakai cookies ini (tidak perlu login lagi)\n")
            return True
            
        except Exception as e:
            print(f"✗ Login manual gagal: {e}")
            print("\nALTERNATIF: Login manual di browser, lalu export cookies")
            return False
    
    def login(self):
        """Login menggunakan cookies"""
        print("Login menggunakan cookies...")
        
        if self.load_cookies():
            # Refresh untuk aktifkan cookies
            self.driver.refresh()
            time.sleep(3)
            
            # Verifikasi login berhasil
            self.driver.get("https://x.com/home")
            time.sleep(3)
            
            if "home" in self.driver.current_url:
                print("✓ Login berhasil dengan cookies!")
                return True
            else:
                print("✗ Cookies expired atau invalid")
                return False
        else:
            print("✗ Cookies tidak ditemukan")
            return False
    
    def navigate_to_target(self):
        """Navigasi ke halaman target berdasarkan mode"""
        from urllib.parse import quote
        
        if self.mode == 1:
            # Mode 1: Home Timeline
            url = "https://x.com/home/"
            print(f"Mode: Home Timeline (Filter keyword: {self.keyword})")
        elif self.mode == 2:
            # Mode 2: Search Top
            encoded_keyword = quote(self.keyword)
            url = f"https://x.com/search?q={encoded_keyword}&src=typed_query"
            print(f"Mode: Search Top (Keyword: {self.keyword})")
        elif self.mode == 3:
            # Mode 3: Search Latest
            encoded_keyword = quote(self.keyword)
            url = f"https://x.com/search?q={encoded_keyword}&src=typed_query&f=live"
            print(f"Mode: Search Latest (Keyword: {self.keyword})")
        
        self.driver.get(url)
        time.sleep(3)
    
    def get_tweet_id(self, tweet_element):
        """Dapatkan ID unik dari tweet"""
        try:
            link = tweet_element.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
            href = link.get_attribute('href')
            tweet_id = href.split('/status/')[-1].split('?')[0]
            return tweet_id
        except:
            return None
    
    def check_required_keyword(self, tweet_element):
        """Cek apakah tweet mengandung keyword yang diperlukan (hanya untuk mode home)"""
        # Hanya untuk mode 1 (home timeline)
        if self.mode != 1:
            return True
        
        if not hasattr(self, 'required_keyword'):
            return True
        
        try:
            tweet_text = tweet_element.text
            if self.required_keyword in tweet_text:
                return True
            else:
                return False
        except:
            return False
    
    def wait_for_tweets_load(self, timeout=10):
        """Tunggu sampai tweet muncul"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            tweets = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            if len(tweets) > 0:
                return True
            time.sleep(1)
        return False

    def is_already_retweeted(self, tweet_element):
        """Cek apakah tweet sudah di-retweet"""
        try:
            tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="unretweet"]')
            return True
        except NoSuchElementException:
            return False
    
    def retweet_tweet(self, tweet_element, tweet_id):
        """Retweet sebuah tweet"""
        try:
            # Scroll ke tweet untuk memastikan visible
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet_element)
            time.sleep(0.5)
            
            # Klik tombol retweet
            retweet_btn = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]')
            
            # Coba klik normal, jika gagal pakai JavaScript
            try:
                retweet_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", retweet_btn)
            
            time.sleep(1)
            
            # Konfirmasi retweet
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))
            )
            
            # Coba klik normal, jika gagal pakai JavaScript
            try:
                confirm_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", confirm_btn)
            
            time.sleep(2)
            
            print(f"✓ Berhasil retweet: {tweet_id}")
            return True
        except Exception as e:
            print(f"✗ Gagal retweet: {e}")
            return False
    
    def scroll_page(self):
        """Scroll halaman untuk load tweet baru"""
        if self.mode == 1:
            # Smooth scroll untuk home timeline
            self.driver.execute_script("""
                let scrollAmount = 500;
                let scrollStep = 15;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount -= scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(1.5)

            self.driver.execute_script("""
                let scrollAmount = 200;
                let scrollStep = -10;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount += scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(0.8)

            self.driver.execute_script("""
                let scrollAmount = 700;
                let scrollStep = 15;
                let scrollInterval = setInterval(() => {
                    window.scrollBy(0, scrollStep);
                    scrollAmount -= scrollStep;
                    if (scrollAmount <= 0) clearInterval(scrollInterval);
                }, 30);
            """)
            time.sleep(2.5)
        else:
            # Simple scroll untuk search
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
                
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(1)
            self.driver.execute_script("window.scrollBy(0, 700);")
            
    def run(self):
        """Jalankan bot secara terus-menerus"""
        try:
            self.setup_driver()
            
            if not self.login():
                print("\n❌ Bot berhenti karena gagal login")
                print("Jalankan: python bot.py atau transfer cookies dari browser untuk self login")
                return
            
            self.navigate_to_target()
            
            print("\n=== Bot mulai berjalan ===")
            if self.mode == 1 and hasattr(self, 'required_keyword'):
                print(f"🔍 Filter aktif: hanya retweet yang mengandung '{self.required_keyword}'")
            print("Tekan Ctrl+C untuk menghentikan\n")
            
            while True:
                # Tunggu tweet load (untuk mode search)
                if self.mode in [2, 3]:
                    if not self.wait_for_tweets_load():
                        print("⏱️ Timeout waiting for tweets, scroll...")
                        self.scroll_page()
                        continue
                
                # Ambil semua tweet di halaman
                tweets = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                if not tweets:
                    print("Tidak ada tweet ditemukan, scroll...")
                    self.scroll_page()
                    continue
                
                for tweet in tweets:
                    try:
                        tweet_id = self.get_tweet_id(tweet)
                        
                        if not tweet_id:
                            continue
                        
                        # Cek apakah sudah pernah di-retweet
                        if self.is_already_retweeted(tweet):
                            print(f"⊘ Skip (sudah di-retweet): {tweet_id}")
                            continue
                        
                        # Cek keyword yang diperlukan (hanya untuk mode home)
                        if not self.check_required_keyword(tweet):
                            continue
                        
                        # Retweet tweet
                        self.retweet_tweet(tweet, tweet_id)
                        time.sleep(3)  # Delay untuk menghindari rate limit
                        
                    except Exception as e:
                        continue
                
                # Scroll untuk mencari tweet baru
                self.scroll_count += 1
                print(f"🔄 Scroll ke-{self.scroll_count}\n")
                self.scroll_page()
                time.sleep(8)
                
        except KeyboardInterrupt:
            print("\n\n✓ Bot dihentikan oleh user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    print("="*50)
    print("BOT RETWEET X (TWITTER) - 3-IN-1")
    print("="*50)
    
    # Cek apakah ada cookies yang tersedia
    bot = TwitterRetweetBot("", 1)
    available_cookies = bot.find_available_cookies()
    
    if not available_cookies:
        print("\n⚠️  COOKIES BELUM ADA!")
        print("Bot akan setup cookies terlebih dahulu...\n")
         
        username = input("Username/Email X: ")
        password = input("Password X: ")
         
        # Dummy bot untuk setup cookies
        bot.setup_driver()
        if bot.manual_login_for_cookies(username, password):
            print("\n✓ Setup selesai! Silakan jalankan bot lagi.\n")
        else:
            print("\n✗ Setup gagal. Silakan coba lagi.\n")
        exit()
    
    # Pilih cookie file
    selected_cookie = bot.select_cookie_file()
    if not selected_cookie:
        exit()
    
    # Menu pilihan mode
    print("\n🎯 PILIH MODE:")
    print("1. Home Timeline (dengan filter keyword)")
    print("2. Search Top (hasil teratas)")
    print("3. Search Latest (terbaru)")
    
    while True:
        try:
            mode = int(input("\nPilih mode (1/2/3): "))
            if mode in [1, 2, 3]:
                break
            else:
                print("❌ Pilih antara 1, 2, atau 3!")
        except ValueError:
            print("❌ Masukkan angka 1, 2, atau 3!")
    
    # Input keyword
    if mode == 1:
        KEYWORD = input("Keyword untuk filter di Home Timeline: ")
    else:
        KEYWORD = input("Keyword pencarian: ")
     
    print("\n" + "="*50)
    
    bot = TwitterRetweetBot(KEYWORD, mode, selected_cookie)
    bot.run()
