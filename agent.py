import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class KanaOmniAgent:
    def __init__(self, username="Kingkana22"):
        self.username = username
        self.base_folder = "knowledge_base"
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)

    def push_to_github(self, commit_message):
        """Melakukan sinkronisasi data ke GitHub secara otomatis"""
        print(f"\n[GITHUB] Memulai sinkronisasi untuk: {self.username}...")
        try:
            # Menggunakan shell=True untuk Windows Compatibility
            subprocess.run(["git", "add", "."], shell=True, check=True)
            subprocess.run(["git", "commit", "-m", commit_message], shell=True, check=True)
            subprocess.run(["git", "push", "origin", "main"], shell=True, check=True)
            print("[GITHUB] SUCCESS: Data telah diabadikan di Cloud.")
        except Exception as e:
            print(f"[GITHUB] FAILED: {e}")
            print("[!] Tips: Pastikan Anda sudah login di browser saat diminta.")

    def scrap_and_learn(self, url):
        """Mesin Scraper untuk belajar niche baru"""
        print(f"\n[*] AGENT MODE: LEARNING")
        print(f"[*] TARGET: {url}")

        # Konfigurasi Chrome Headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            time.sleep(5) # Memberi waktu untuk rendering JavaScript

            # Ekstraksi Data
            title = driver.title.replace("/", "-").replace(" ", "_")
            body_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Cleaning nama file dari karakter ilegal
            clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).rstrip()
            
            # Simpan File Lokal
            timestamp = int(time.time())
            filename = f"research_{clean_title}_{timestamp}.md"
            filepath = os.path.join(self.base_folder, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# RESEARCH DATA: {title}\n")
                f.write(f"SOURCE URL: {url}\n")
                f.write(f"DATE: {time.ctime()}\n")
                f.write("-" * 50 + "\n\n")
                f.write(body_text)

            print(f"[+] SUCCESS: Data niche disimpan di {filepath}")
            
            # Jalankan Auto-Sync
            self.push_to_github(f"Omni-Learn: {clean_title}")

        except Exception as e:
            print(f"[!] ERROR SAAT SCRAPPING: {e}")
        finally:
            driver.quit()

    def run(self):
        """Interface utama Agent"""
        print("="*60)
        print(f"   KANA OMNI-AGENT V1.0 | OPERATOR: {self.username}")
        print("   Status: FULLY INTEGRATED WITH GITHUB MAIN")
        print("="*60)

        while True:
            print("\nMENU:")
            print("1. Scrap Niche Baru (Learn & Sync)")
            print("2. Exit")
            
            choice = input("\n[KANA]> Pilih menu (1/2): ")

            if choice == "1":
                target_url = input("[?] Masukkan URL Niche/Target: ")
                if target_url.startswith("http"):
                    self.scrap_and_learn(target_url)
                else:
                    print("[!] Error: Masukkan URL lengkap dengan http:// atau https://")
            elif choice == "2":
                print("[*] Shutting down agent. Sampai jumpa, Kingkana.")
                break
            else:
                print("[!] Pilihan tidak valid.")

if __name__ == "__main__":
    agent = KanaOmniAgent()
    agent.run()