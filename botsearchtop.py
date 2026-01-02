#!/usr/bin/env python3
"""
Bot Retweet X (Twitter) untuk Termux - Cookie Based Login
Lebih stabil dan reliable!
"""

import time
import json
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TwitterRetweetBot:
    def __init__(self, keyword, cookies_file='twitter_cookies.pkl'):
        self.keyword = keyword
        self.cookies_file = cookies_file
        self.retweeted_ids = self.load_retweeted_ids()
        self.driver = None
        
    def load_retweeted_ids(self):
        """Load daftar tweet yang sudah di-retweet"""
        if os.path.exists('retweeted_ids.json'):
            with open('retweeted_ids.json', 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_retweeted_ids(self):
        """Simpan daftar tweet yang sudah di-retweet"""
        with open('retweeted_ids.json', 'w') as f:
            json.dump(list(self.retweeted_ids), f)
    
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
            # Buka Twitter dulu sebelum load cookies
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
            # Input username
            print("Isi username...")
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.send_keys(username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Input password
            print("Isi password...")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Tunggu sampai login berhasil
            print("Menunggu login selesai...")
            time.sleep(10)
            
            # Simpan cookies
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
    
    def search_keyword(self):
        """Cari tweet dengan keyword"""
        from urllib.parse import quote
        encoded_keyword = quote(self.keyword)
        search_url = f"https://x.com/search?q={encoded_keyword}&src=typed_query"
        print(f"Mencari keyword: {self.keyword}")
        self.driver.get(search_url)
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
            # Klik tombol retweet
            retweet_btn = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]')
            retweet_btn.click()
            time.sleep(1)
            
            # Konfirmasi retweet
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))
            )
            confirm_btn.click()
            time.sleep(2)
            
            print(f"✓ Berhasil retweet: {tweet_id}")
            self.retweeted_ids.add(tweet_id)
            self.save_retweeted_ids()
            return True
        except Exception as e:
            print(f"✗ Gagal retweet {tweet_id}: {e}")
            return False
    
    def scroll_page(self):
        """Scroll halaman untuk load tweet baru - smooth scroll seperti manusia menggunakan mouse wheel"""
        # Scroll smooth seperti mouse wheel untuk trigger lazy loading
        self.driver.execute_script("""
            let scrollAmount = 500;
            let scrollStep = 15;
            let scrollInterval = setInterval(() => {
                window.scrollBy(0, scrollStep);
                scrollAmount -= scrollStep;
                if (scrollAmount <= 0) clearInterval(scrollInterval);
            }, 30);
        """)
        time.sleep(1.5)  # Tunggu scroll selesai

        # Scroll balik sedikit (trick untuk trigger reload) dengan smooth
        self.driver.execute_script("""
            let scrollAmount = 200;
            let scrollStep = -10;
            let scrollInterval = setInterval(() => {
                window.scrollBy(0, scrollStep);
                scrollAmount += scrollStep;  // Karena scrollStep negatif
                if (scrollAmount <= 0) clearInterval(scrollInterval);
            }, 30);
        """)
        time.sleep(0.8)

        # Scroll maju lagi
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
            
    def run(self):
        """Jalankan bot secara terus-menerus"""
        try:
            self.setup_driver()
            
            if not self.login():
                print("\n❌ Bot berhenti karena gagal login")
                print("Jalankan: python setup_cookies.py untuk setup cookies dulu")
                return
            
            self.search_keyword()
            
            print("\n=== Bot mulai berjalan ===")
            print("Tekan Ctrl+C untuk menghentikan\n")
            
            scroll_count = 0
            processed_in_session = set()
            
            while True:
                # Tunggu tweet load
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
                        
                        # Skip jika sudah diproses di session ini
                        if tweet_id in processed_in_session:
                            continue
                        
                        processed_in_session.add(tweet_id)
                        
                        # Cek apakah sudah pernah di-retweet
                        if tweet_id in self.retweeted_ids or self.is_already_retweeted(tweet):
                            print(f"⊘ Skip (sudah di-retweet): {tweet_id}")
                            continue
                        
                        # Retweet tweet baru
                        self.retweet_tweet(tweet, tweet_id)
                        time.sleep(3)  # Delay untuk menghindari rate limit
                        
                    except Exception as e:
                        print(f"Error memproses tweet: {e}")
                        continue
                
                # Scroll untuk mencari tweet baru
                scroll_count += 1
                
                # COUNTER REAL-TIME (PASTE DI SINI)
                print(f"\n📊 Stats: ✓{len(self.retweeted_ids)} retweet | 🔄Scroll-{scroll_count}\n")
                
                self.scroll_page()
                time.sleep(8)
                
        except KeyboardInterrupt:
            print("\n\n✓ Bot dihentikan oleh user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            print(f"\n📊 Total tweet yang di-retweet: {len(self.retweeted_ids)}")

if __name__ == "__main__":
    print("="*50)
    print("BOT RETWEET X (x) - TERMUX")
    print("="*50)
    
    # Cek apakah cookies sudah ada
    if not os.path.exists('twitter_cookies.pkl'):
        print("\n⚠️  COOKIES BELUM ADA!")
        print("Jalankan setup cookies dulu:\n")
        print("1. python setup_cookies.py")
        print("   (untuk login dan simpan cookies)\n")
        print("2. python bot_retweet.py")
        print("   (untuk jalankan bot)\n")
        
        choice = input("Mau setup cookies sekarang? (y/n): ")
        if choice.lower() == 'y':
            username = input("Username/Email X: ")
            password = input("Password X: ")
            keyword = input("Keyword pencarian: ")
            
            bot = TwitterRetweetBot(keyword)
            bot.setup_driver()
            if bot.manual_login_for_cookies(username, password):
                print("\n✓ Setup selesai! Jalankan bot lagi:")
                print("python bot_retweet.py\n")
        exit()
    
    # Jalankan bot dengan cookies yang sudah ada
    KEYWORD = input("Keyword pencarian: ")
    
    print("\n" + "="*50)
    
    bot = TwitterRetweetBot(KEYWORD)
    bot.run()
