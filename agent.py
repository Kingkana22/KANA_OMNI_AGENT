import os
import time
import random
import subprocess
import threading
import queue
import shutil
from datetime import datetime

# Fix distutils for Python 3.12+
try:
    from distutils.version import LooseVersion
except ImportError:
    try:
        from setuptools._distutils.version import LooseVersion
    except ImportError:
        def LooseVersion(v): return v

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

class AgentCore:
    def __init__(self):
        self.kb_dir = "knowledge_base"
        self.victim_dir = "cloned_repos"
        self.log_dir = "logs"
        # Fokus keyword untuk audit Smart Contract
        self.target_keywords = ["selfdestruct", "delegatecall", "tx.origin", "reentrancy", "withdraw"]
        self.max_threads = 5 # Turunkan thread untuk stabilitas driver di Windows
        
        for d in [self.kb_dir, self.victim_dir, self.log_dir]:
            os.makedirs(d, exist_ok=True)

    def get_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            # Bypass detection
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            options.add_argument(f"--user-agent={ua}")
            
            driver = uc.Chrome(options=options)
            return driver
        except:
            return None

    def get_targets_from_kb(self):
        targets = []
        if not os.path.exists(self.kb_dir):
            return targets
        
        for f in os.listdir(self.kb_dir):
            if f.endswith(".md"):
                try:
                    with open(os.path.join(self.kb_dir, f), "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                        if any(k in content.lower() for k in self.target_keywords):
                            for line in content.splitlines():
                                if "github.com" in line:
                                    # Extract URL secara presisi
                                    if "http" in line:
                                        url = "http" + line.split("http")[1].split(" ")[0].split(")")[0].strip()
                                        if url not in targets:
                                            targets.append(url)
                except: continue
        return targets

    def clone_repo(self, url):
        try:
            # Normalisasi URL ke .git
            repo_base = url.split("/blob/")[0] if "/blob/" in url else url.rstrip("/")
            repo_base = repo_base.split("/tree/")[0] if "/tree/" in repo_base else repo_base
            if not repo_base.endswith(".git"):
                repo_base += ".git"
            
            repo_name = repo_base.split("/")[-1].replace(".git", "")
            target_path = os.path.join(self.victim_dir, repo_name)
            
            if os.path.exists(target_path):
                return

            # Silent clone
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(["git", "clone", "--depth=1", repo_base, target_path], 
                           env=env, capture_output=True, timeout=60)
        except:
            pass

    def process_target(self, url):
        driver = self.get_driver()
        if not driver:
            return
        try:
            driver.get(url)
            time.sleep(random.uniform(7, 12))
            
            source = driver.page_source
            ts = int(time.time())
            # Simpan hasil scan baru
            with open(os.path.join(self.kb_dir, f"audit_{ts}.md"), "w", encoding="utf-8") as f:
                f.write(f"URL: {url}\nDATE: {datetime.now()}\n\n{source[:30000]}")
            
            if "github.com" in url:
                self.clone_repo(url)
        except:
            pass
        finally:
            try:
                driver.close()
                driver.quit()
            except:
                pass

    def sync(self):
        # Force cleaning sebelum push
        try:
            subprocess.run(["git", "add", "."], shell=True)
            subprocess.run(["git", "commit", "-m", f"Audit_Update_{int(time.time())}"], shell=True)
            subprocess.run(["git", "push", "origin", "main", "--force"], shell=True)
        except:
            pass

    def run(self):
        print(f"[*] Starting Silent Audit...")
        targets = self.get_targets_from_kb()
        if not targets:
            print("[!] No targets found in knowledge base.")
            return

        print(f"[*] Found {len(targets)} targets. Executing...")
        
        # Eksekusi sekuensial atau thread kecil untuk menghindari WinError 6
        for url in targets[:15]:
            self.process_target(url)
            print(f"[+] Processed: {url}")

        self.sync()
        print("[*] All tasks synced to GitHub.")

if __name__ == "__main__":
    AgentCore().run()