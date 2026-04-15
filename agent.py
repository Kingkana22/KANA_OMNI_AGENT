import os
import time
import subprocess
import threading
import random
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

class AgentCore:
    def __init__(self):
        self.kb_dir = "knowledge_base"
        self.victim_dir = "cloned_repos"
        # Pola kode yang merupakan "Lubang Uang"
        self.money_leaks = {
            "REENTRANCY": ".call{value:",
            "UNPROTECTED": "function withdraw",
            "DELEGATE": "delegatecall",
            "OWNER_CHANGE": "transferOwnership",
            "MINT_SPOOF": "mint("
        }
        for d in [self.kb_dir, self.victim_dir]:
            os.makedirs(d, exist_ok=True)

    def get_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            return uc.Chrome(options=options)
        except: return None

    def analyze_cuan(self, local_path):
        """Menyisir file .sol yang baru di-clone untuk mencari celah uang"""
        for root, _, files in os.walk(local_path):
            for file in files:
                if file.endswith(".sol"):
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                for bug, pattern in self.money_leaks.items():
                                    if pattern in line:
                                        print(f"💰 [CUAN FOUND] {bug} in {file} (L:{i}) -> {line.strip()}")
                    except: pass

    def clone_repo(self, url):
        repo_base = url.split("/blob/")[0] if "/blob/" in url else url.rstrip("/")
        if not repo_base.endswith(".git"): repo_base += ".git"
        
        repo_name = repo_base.split("/")[-1].replace(".git", "")
        target_path = os.path.join(self.victim_dir, repo_name)
        
        if not os.path.exists(target_path):
            print(f"[*] Cloning {repo_name}...")
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(["git", "clone", "--depth=1", repo_base, target_path], 
                           env=env, capture_output=True)
            # Langsung analisa setelah clone
            self.analyze_cuan(target_path)

    def process_target(self, url):
        driver = self.get_driver()
        if not driver: return
        try:
            driver.get(url)
            time.sleep(10)
            if "github.com" in url: self.clone_repo(url)
        finally:
            try: driver.quit()
            except: pass

    def sync(self):
        subprocess.run(["git", "add", "."], shell=True)
        subprocess.run(["git", "commit", "-m", f"Audit_{int(time.time())}"], shell=True)
        subprocess.run(["git", "push", "origin", "main", "--force"], shell=True)

    def run(self):
        # Ambil URL dari knowledge_base secara otomatis
        targets = []
        for f in os.listdir(self.kb_dir):
            if f.endswith(".md"):
                with open(os.path.join(self.kb_dir, f), "r", encoding="utf-8", errors="ignore") as file:
                    for line in file:
                        if "github.com" in line and "http" in line:
                            targets.append("http" + line.split("http")[1].split(" ")[0].strip())

        for url in list(set(targets))[:5]:
            print(f"[*] Attacking: {url}")
            self.process_target(url)
        
        self.sync()

if __name__ == "__main__":
    AgentCore().run()