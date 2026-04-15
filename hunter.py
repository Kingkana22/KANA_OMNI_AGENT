import os
import requests
import time
from notifier import send_kana_alert

class KanaHunter:
    def __init__(self):
        # Pola pencarian celah/data bocor
        self.dorks = [
            "filename:.env DB_PASSWORD",
            "extension:sol 'selfdestruct'",
            "extension:sol 'delegatecall'",
            "filename:config.php 'password'",
            "path:knowledge_base 'vulnerability'"
        ]
        self.github_token = os.getenv("GITHUB_TOKEN") # Opsional, untuk rate limit lebih tinggi

    def hunt_github(self):
        print("\n" + "="*40)
        print("   KANA CORE: HUNTER MODE ACTIVE")
        print("="*40)
        
        for query in self.dorks:
            print(f"[*] Searching for: {query}")
            # Simulasi pencarian via API atau Scraper
            # Untuk versi ini, kita integrasikan dengan hasil scrap yang sudah ada
            # agar tetap aman dan legal (Passive Hunting)
            
            # Logic: Hunter akan menyisir folder knowledge_base Anda 
            # untuk mencari 'Exploit yang bisa langsung dipakai'
            self.internal_audit(query)
            time.sleep(2)

    def internal_audit(self, query):
        kb_path = "knowledge_base"
        files = [f for f in os.listdir(kb_path) if f.endswith('.md')]
        
        for file in files:
            with open(os.path.join(kb_path, file), 'r', encoding='utf-8') as f:
                content = f.read()
                if query.split()[-1].strip("'") in content:
                    msg = f"🎯 TARGET IDENTIFIED: {file}\nPattern: {query}\nStatus: Ready for Audit."
                    print(f"[!] {msg}")
                    send_kana_alert(msg)

if __name__ == "__main__":
    hunter = KanaHunter()
    hunter.hunt_github()