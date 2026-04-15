import os
import time
import requests
import subprocess
from datetime import datetime

class BSCSniper:
    def __init__(self):
        # API Key yang kamu berikan
        self.api_key = "AN4M57CM4CIDF24EE3AP2G9H2BBEFQVC6E" 
        self.kb_dir = "knowledge_base"
        self.log_dir = "logs"
        self.log_file = os.path.join(self.log_dir, "money_found.log")
        self.base_url = "https://api.bscscan.com/api"
        
        for d in [self.kb_dir, self.log_dir]:
            os.makedirs(d, exist_ok=True)

    def get_latest_contracts(self):
        """Ambil list transaksi terbaru untuk mencari alamat kontrak fresh"""
        print(f"[*] [{datetime.now().strftime('%H:%M:%S')}] Scanning BSC for new targets...")
        params = {
            "module": "account",
            "action": "txlist",
            "address": "0x0000000000000000000000000000000000000000",
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": 25,
            "sort": "desc",
            "apikey": self.api_key
        }
        try:
            r = requests.get(self.base_url, params=params, timeout=10)
            data = r.json()
            if data["status"] == "1":
                # Filter hanya transaksi yang membuat kontrak (to adalah kosong atau kontrak baru)
                return list(set([tx["to"] for tx in data["result"] if tx["to"] != ""]))
        except Exception as e:
            print(f"[!] API Error: {e}")
        return []

    def audit_contract(self, address):
        """Tarik source code dan cari celah withdraw/bocor"""
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": self.api_key
        }
        try:
            r = requests.get(self.base_url, params=params, timeout=10)
            res = r.json()
            if res["status"] == "1" and res["result"]:
                source = res["result"][0].get("SourceCode", "")
                if not source or len(source) < 100: return # Skip jika tidak ada source code
                
                # Pola Cuan: Fungsi withdraw/transfer tanpa proteksi 'onlyOwner'
                target_patterns = ["withdraw(", "transfer(", "payable", "selfdestruct", "call{value:"]
                
                for pattern in target_patterns:
                    if pattern in source.lower():
                        # Cek filter keamanan paling fatal
                        if "onlyowner" not in source.lower() and "require(msg.sender" not in source.lower():
                            print(f"💰 [CUAN DETECTED] Address: {address} | Reason: No Protection on {pattern}")
                            
                            # Simpan log ke file lokal
                            with open(self.log_file, "a") as f:
                                f.write(f"[{datetime.now()}] ADDRESS: {address} | PATTERN: {pattern}\n")
                            
                            # Simpan source kodenya ke KB untuk bukti/eksekusi
                            with open(os.path.join(self.kb_dir, f"TARGET_{address}.sol"), "w", encoding="utf-8") as f:
                                f.write(source)
                            return
        except:
            pass

    def sync(self):
        """Push hasil temuan ke GitHub Kingkana22"""
        try:
            subprocess.run(["git", "add", "."], shell=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Audit_Update_{int(time.time())}"], shell=True, capture_output=True)
            subprocess.run(["git", "push", "origin", "main", "--force"], shell=True, capture_output=True)
            print("[*] Results synced to Cloud.")
        except:
            pass

    def run(self):
        print("=== 💀 KANA OMNI-REAPER BSC SNIPER ACTIVE 💀 ===")
        print(f"[*] API KEY LOADED: {self.api_key[:5]}...{self.api_key[-5:]}")
        
        while True:
            addresses = self.get_latest_contracts()
            if addresses:
                for addr in addresses:
                    self.audit_contract(addr)
                    time.sleep(0.2) # Jeda agar tidak kena limit rate API
            
            self.sync()
            # Jeda antar scan agar tidak spamming API
            print("[*] Cycle complete. Waiting for new blocks...")
            time.sleep(30)

if __name__ == "__main__":
    try:
        BSCSniper().run()
    except KeyboardInterrupt:
        print("\n[!] Reaper Stopped.")