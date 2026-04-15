import os, time, requests, subprocess, threading, queue
from datetime import datetime

class KanaOmniReaper:
    def __init__(self):
        self.api_key = "AN4M57CM4CIDF24EE3AP2G9H2BBEFQVC6E"
        self.log_file = "logs/money_found.log"
        self.base_url = "https://api.bscscan.com/api"
        self.target_queue = queue.Queue()
        self.workers = 8 # Jumlah bot pencari
        os.makedirs("logs", exist_ok=True)

    def get_new_contracts(self):
        """Bot Utama: Ngintip blok terbaru BSC"""
        while True:
            params = {"module":"account","action":"txlist","address":"0x0000000000000000000000000000000000000000","page":1,"offset":25,"sort":"desc","apikey":self.api_key}
            try:
                r = requests.get(self.base_url, params=params, timeout=10).json()
                if r["status"] == "1":
                    for tx in r["result"]:
                        if tx["to"]: self.target_queue.put(tx["to"])
            except: pass
            time.sleep(10)

    def audit_engine(self):
        """Bot Pekerja: Bedah kode nyari celah withdraw"""
        while True:
            addr = self.target_queue.get()
            time.sleep(1.5) # Jeda biar gak di-ban BscScan
            params = {"module":"contract","action":"getsourcecode","address":addr,"apikey":self.api_key}
            try:
                r = requests.get(self.base_url, params=params, timeout=10).json()
                if r["status"] == "1" and r["result"]:
                    src = r["result"][0].get("SourceCode", "")
                    # LOGIKA CUAN: No Owner + Ada fungsi tarik duit
                    if src and "onlyowner" not in src.lower():
                        if any(x in src.lower() for x in ["withdraw(", ".call{value:", "payable"]):
                            print(f"💰 [DAPET] {addr}")
                            with open(self.log_file, "a") as f:
                                f.write(f"[{datetime.now()}] FOUND: {addr}\n")
            except: pass
            self.target_queue.task_done()

    def cloud_sync(self):
        """Bot Kurir: Kirim hasil ke GitHub Kingkana22"""
        while True:
            time.sleep(120)
            subprocess.run("git add . && git commit -m 'Sniper_Update' && git push origin main --force", shell=True)
            print("[*] Cloud Synced.")

    def run(self):
        print(f"=== 💀 KANA REAPER ACTIVE (8 WORKERS) 💀 ===")
        threading.Thread(target=self.get_new_contracts, daemon=True).start()
        threading.Thread(target=self.cloud_sync, daemon=True).start()
        for _ in range(self.workers):
            threading.Thread(target=self.audit_engine, daemon=True).start()
        while True: time.sleep(1)

if __name__ == "__main__":
    KanaOmniReaper().run()