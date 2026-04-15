import os
import time
import requests
import subprocess
import threading
import queue
from datetime import datetime

class BarbarSniper:
    def __init__(self):
        self.api_key = "AN4M57CM4CIDF24EE3AP2G9H2BBEFQVC6E"
        self.kb_dir = "knowledge_base"
        self.log_file = "logs/money_found.log"
        self.base_url = "https://api.bscscan.com/api"
        self.target_queue = queue.Queue()
        self.max_workers = 8  # 8 Worker sudah cukup agresif untuk API gratis
        
        for d in [self.kb_dir, "logs"]:
            os.makedirs(d, exist_ok=True)

    def fetch_targets(self):
        """Mencari alamat kontrak baru dari blok terakhir"""
        while True:
            params = {
                "module": "account", "action": "txlist",
                "address": "0x0000000000000000000000000000000000000000",
                "page": 1, "offset": 30, "sort": "desc", "apikey": self.api_key
            }
            try:
                r = requests.get(self.base_url, params=params, timeout=10)
                data = r.json()
                if data["status"] == "1":
                    addrs = list(set([tx["to"] for tx in data["result"] if tx["to"] != ""]))
                    for a in addrs:
                        self.target_queue.put(a)
            except: pass
            time.sleep(10) # Ambil blok baru tiap 10 detik

    def auditor_worker(self):
        """Worker yang melakukan audit kode"""
        while True:
            address = self.target_queue.get()
            if address:
                # Jeda antar worker agar tidak melebihi 5 req/sec (Rate Limit)
                time.sleep(2) 
                params = {
                    "module": "contract", "action": "getsourcecode",
                    "address": address, "apikey": self.api_key
                }
                try:
                    r = requests.get(self.base_url, params=params, timeout=10)
                    res = r.json()
                    
                    # Cek jika kena limit
                    if "Max rate limit" in str(res.get("result", "")):
                        time.sleep(5)
                        self.target_queue.put(address) # Antre ulang
                        continue

                    if res["status"] == "1" and res["result"]:
                        source = res["result"][0].get("SourceCode", "")
                        if source and len(source) > 200:
                            # Logika deteksi cuan
                            if "onlyowner" not in source.lower():
                                if any(p in source.lower() for p in ["withdraw(", "call{value:", "payable"]):
                                    print(f"💰 [POTENSI REAL] {address}")
                                    with open(self.log_file, "a") as f:
                                        f.write(f"[{datetime.now()}] FOUND: {address}\n")
                except: pass
            self.target_queue.task_done()

    def sync_loop(self):
        """Kirim hasil ke GitHub tiap 3 menit"""
        while True:
            time.sleep(180)
            try:
                subprocess.run(["git", "add", "."], shell=True)
                subprocess.run(["git", "commit", "-m", "Auto_Update_Scan"], shell=True)
                subprocess.run(["git", "push", "origin", "main", "--force"], shell=True)
                print("[*] Logs Synced to GitHub.")
            except: pass

    def run(self):
        print(f"=== 💀 KANA REAPER ACTIVE (Workers: {self.max_workers}) 💀 ===")
        # Start Threads
        threading.Thread(target=self.fetch_targets, daemon=True).start()
        threading.Thread(target=self.sync_loop, daemon=True).start()
        
        for _ in range(self.max_workers):
            threading.Thread(target=self.auditor_worker, daemon=True).start()
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    BarbarSniper().run()