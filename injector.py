import os
import requests
import subprocess
import time
from bs4 import BeautifulSoup

class TopicScraper:
    def __init__(self):
        # Link topic yang ingin kamu sikat
        self.topic_url = "https://github.com/topics/hacking-tools?l=html"
        self.kb_dir = "knowledge_base/reference_codes"
        os.makedirs(self.kb_dir, exist_ok=True)

    def get_repo_links(self):
        print(f"[*] Scanning Topic: {self.topic_url}")
        repos = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(self.topic_url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Mencari elemen link repository di halaman topic
            links = soup.find_all('a', class_='text-bold wb-break-word')
            for link in links:
                repo_path = link.get('href').strip()
                full_url = f"https://github.com{repo_path}.git"
                repos.append(full_url)
        except Exception as e:
            print(f"[!] Error scanning topic: {e}")
        return list(set(repos))

    def inject(self):
        print("=== 🧠 STARTING TOPIC INJECTION ===\n")
        
        repo_list = self.get_repo_links()
        print(f"[+] Found {len(repo_list)} repositories in this topic.\n")

        for repo in repo_list:
            repo_name = repo.split("/")[-1].replace(".git", "")
            target_path = os.path.join(self.kb_dir, repo_name)
            
            if not os.path.exists(target_path):
                print(f"[*] Cloning {repo_name}...")
                # Clone dengan --depth=1 agar cepat dan hemat space
                subprocess.run(["git", "clone", "--depth=1", repo, target_path], capture_output=True)
                
                # WAJIB: Hapus .git di dalam agar tidak error saat push ke Kingkana22
                git_folder = os.path.join(target_path, ".git")
                if os.path.exists(git_folder):
                    subprocess.run(f"rmdir /s /q \"{git_folder}\"", shell=True)
            else:
                print(f"[-] {repo_name} already exists.")

        self.sync_to_github()

    def sync_to_github(self):
        print("\n[*] Syncing all new knowledge to Cloud...")
        subprocess.run("git add . && git commit -m 'Topic_Discovery_Update' && git push origin main --force", shell=True)
        print("[!] All set. Sniper is now much more dangerous.")

if __name__ == "__main__":
    # Pastikan library BeautifulSoup terinstall: pip install beautifulsoup4
    TopicScraper().inject()