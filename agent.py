import os
import time
import random
import subprocess
import threading
import queue
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
        self.target_keywords = ["selfdestruct", "delegatecall", "tx.origin", "reentrancy", "withdraw"]
        self.max_threads = 10
        self.q = queue.Queue()
        
        for d in [self.kb_dir, self.victim_dir, self.log_dir]:
            os.makedirs(d, exist_ok=True)

    def get_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        # Anti-detection bypass
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        options.add_argument(f"--user-agent={ua}")
        
        driver = uc.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
        return driver

    def get_targets_from_kb(self):
        targets = []
        if not os.path.exists(self.kb_dir):
            return targets
        
        for f in os.listdir(self.kb_dir):
            if f.endswith(".md"):
                with open(os.path.join(self.kb_dir, f), "r", encoding="utf-8") as file:
                    content = file.read()
                    if any(k in content.lower() for k in self.target_keywords):
                        for line in content.splitlines():
                            if "github.com" in line:
                                parts = line.split("http")
                                if len(parts) > 1:
                                    url = "http" + parts[1].split(" ")[0].split(")")[0].strip()
                                    if url not in targets:
                                        targets.append(url)
        return targets

    def clone_repo(self, url):
        try:
            repo_base = url.split("/blob/")[0] if "/blob/" in url else url.rstrip("/")
            if not repo_base.endswith(".git"):
                repo_base += ".git"
            
            repo_name = repo_base.split("/")[-1].replace(".git", "")
            target_path = os.path.join(self.victim_dir, repo_name)
            
            if os.path.exists(target_path):
                return

            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(["git", "clone", "--depth=1", repo_base, target_path], 
                           env=env, capture_output=True, timeout=60)
        except:
            pass

    def process_target(self, url):
        driver = None
        try:
            driver = self.get_driver()
            driver.get(url)
            time.sleep(random.uniform(5, 10))
            
            source = driver.page_source
            ts = int(time.time())
            with open(os.path.join(self.kb_dir, f"scan_{ts}.md"), "w", encoding="utf-8") as f:
                f.write(f"URL: {url}\n\n{source[:20000]}")
            
            if "github.com" in url:
                self.clone_repo(url)
        except:
            pass
        finally:
            if driver:
                driver.quit()

    def sync(self):
        try:
            subprocess.run(["git", "add", "."], shell=True)
            subprocess.run(["git", "commit", "-m", "update_" + str(int(time.time()))], shell=True)
            subprocess.run(["git", "push", "origin", "main", "--force"], shell=True)
        except:
            pass

    def run(self):
        targets = self.get_targets_from_kb()
        if not targets:
            return

        threads = []
        for url in targets[:20]:
            t = threading.Thread(target=self.process_target, args=(url,))
            t.start()
            threads.append(t)
            time.sleep(1)

        for t in threads:
            t.join()
        
        self.sync()

if __name__ == "__main__":
    AgentCore().run()