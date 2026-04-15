import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def push_to_github(message):
    try:
        subprocess.run(["git", "add", "."], shell=True, check=True)
        subprocess.run(["git", "commit", "-m", message], shell=True, check=True)
        subprocess.run(["git", "push", "origin", "master"], shell=True, check=True)
        print("[✔] Sinkronisasi GitHub Kingkana22 Berhasil.")
    except Exception as e:
        print(f"[!] Gagal Push: {e}. Pastikan Git sudah terinstall dan Repo sudah di-link.")

def start_kana_agent():
    print("\n" + "="*50)
    print("   KANA OMNI-AGENT V1.0 | USER: Kingkana22")
    print("="*50)
    
    target_url = input("[?] Masukkan URL Niche/Target Belajar: ")
    
    if not target_url.startswith("http"):
        print("[!] URL Salah!")
        return

    print(f"[*] Memulai Scrapping Niche...")
    opts = Options()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

    try:
        driver.get(target_url)
        time.sleep(5)
        
        data = driver.find_element(By.TAG_NAME, "body").text
        title = driver.title.replace("/", "-")
        
        # Simpan Knowledge
        if not os.path.exists("knowledge_base"): os.makedirs("knowledge_base")
        file_path = f"knowledge_base/data_{int(time.time())}.md"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# SOURCE: {target_url}\n\n{data}")
        
        print(f"[+] Data terserap ke {file_path}")
        
        # Auto-Sync
        push_to_github(f"Bot Learn: {title}")
        
    except Exception as e:
        print(f"[X] Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_kana_agent()