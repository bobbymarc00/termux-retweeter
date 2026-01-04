#!/usr/bin/env python3
"""
Convert cookies dari berbagai format ke format bot
"""

import json
import pickle
import re

def parse_netscape_cookies(content):
    """Parse Netscape/curl format cookies"""
    cookies = []
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split('\t')
        if len(parts) >= 7:
            cookies.append({
                'name': parts[5],
                'value': parts[6],
                'domain': parts[0],
                'path': parts[2],
                'secure': parts[3] == 'TRUE',
                'httpOnly': False
            })
    return cookies

def parse_json_cookies(content):
    """Parse JSON format cookies"""
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Convert dict to list
            return [{'name': k, 'value': v, 'domain': '.x.com'} for k, v in data.items()]
    except:
        return []

def parse_raw_text(content):
    """Parse dari raw text dengan pattern name=value"""
    cookies = []
    
    # Cari auth_token
    auth_match = re.search(r'auth_token["\s:=]+([a-f0-9]+)', content)
    if auth_match:
        cookies.append({
            'name': 'auth_token',
            'value': auth_match.group(1),
            'domain': '.x.com',
            'path': '/',
            'secure': True,
            'httpOnly': True
        })
    
    # Cari ct0
    ct0_match = re.search(r'ct0["\s:=]+([a-f0-9]+)', content)
    if ct0_match:
        cookies.append({
            'name': 'ct0',
            'value': ct0_match.group(1),
            'domain': '.x.com',
            'path': '/',
            'secure': True,
            'httpOnly': False
        })
    
    return cookies

def convert_cookies():
    print("="*50)
    print("CONVERT COOKIES")
    print("="*50)
    
    # Pilih nama file output
    print("\n📁 PILIH NAMA FILE OUTPUT:")
    print("1. twitter_cookies.pkl (default)")
    print("2. cookies1.pkl")
    print("3. cookies2.pkl")
    print("4. cookies3.pkl")
    print("5. cookies4.pkl")
    print("6. cookies5.pkl")
    
    while True:
        try:
            choice = int(input("\nPilih nama file output (1-6): "))
            if 1 <= choice <= 6:
                if choice == 1:
                    output_file = 'twitter_cookies.pkl'
                else:
                    output_file = f'cookies{choice-1}.pkl'
                break
            else:
                print("❌ Pilih antara 1 sampai 6!")
        except ValueError:
            print("❌ Masukkan angka 1 sampai 6!")
    
    # Baca file
    try:
        with open('cookies_raw.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("\n❌ File cookies_raw.txt tidak ditemukan!")
        print("Pastikan file ada di folder yang sama")
        return
    
    print(f"\n📄 File size: {len(content)} bytes")
    print(f"📄 Preview (100 char): {content[:100]}...\n")
    
    # Deteksi format
    cookies = []
    
    if content.strip().startswith('[') or content.strip().startswith('{'):
        print("🔍 Detected: JSON format")
        cookies = parse_json_cookies(content)
    elif '\t' in content and 'TRUE' in content.upper():
        print("🔍 Detected: Netscape format")
        cookies = parse_netscape_cookies(content)
    else:
        print("🔍 Detected: Raw text format")
        cookies = parse_raw_text(content)
    
    if not cookies:
        print("\n❌ Tidak ada cookies yang berhasil di-parse!")
        print("\n💡 Coba manual:")
        print("   python setup_cookies_manual.py")
        return
    
    # Filter hanya cookies penting
    important_cookies = []
    for cookie in cookies:
        if cookie.get('name') in ['auth_token', 'ct0', 'twid', 'att']:
            important_cookies.append(cookie)
    
    if important_cookies:
        cookies = important_cookies
    
    # Simpan
    with open(output_file, 'wb') as f:
        pickle.dump(cookies, f)
    
    print(f"\n✅ Berhasil convert {len(cookies)} cookies!")
    print("\n📋 Cookies yang disimpan:")
    for c in cookies:
        value_preview = c.get('value', '')[:20]
        print(f"   ✓ {c.get('name')}: {value_preview}...")
    
    print(f"\n📁 Saved to: {output_file}")
    print("\n🚀 Sekarang jalankan bot:")
    print("   python bot.py\n")

if __name__ == "__main__":
    convert_cookies()
