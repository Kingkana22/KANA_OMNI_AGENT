import os
import subprocess
import time

class KnowledgeInjector:
    def __init__(self):
        # Daftar sumber ilmu kelas kakap
        self.targets = [
            "https://github.com/SunWeb3Sec/DeFiHackLabs",
            "https://github.com/QuillHash/Smart-Contract-Attack-Vectors",
            "https://github.com/pcaversaccio/re-f3-wiki",
            "https://github.com/pwnCustard/smart-contract-bugs"
        ]
        self.kb_dir = "knowledge_base/reference_codes"
        os.makedirs(self.kb_dir, exist_ok=True)

    def inject(self):
        print("=== 🧠 STARTING KNOWLEDGE INJECTION ===\n")
        for repo in self.targets:
            repo_name = repo.split("/")[-1]
            target_path = os.path.join(self.kb_dir, repo_name)
            
            if os.path.exists(target_path):
                print(f"[*] {repo_name} already exists. Updating...")
                subprocess.run(["git", "-C", target_path, "pull"], capture_output=True)
            else:
                print(f"[*] Downloading {repo_name}...")
                subprocess.run(["git", "clone", "--depth=1", repo, target_path], capture_output=True)
            
            # Cari file .sol (Smart Contract) di dalam repo tersebut untuk referensi sniper
            self.extract_patterns(target_path)
        
        self.sync_to_github()

    def extract_patterns(self, path):
        """Menghitung berapa banyak contoh kode yang berhasil disedot"""
        count = 0
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".sol"):
                    count += 1
        print(f"[+] Successfully indexed {count} solidity patterns from this source.")

    def sync_to_github(self):
        print("\n[*] Syncing knowledge to Kingkana22 Cloud...")
        subprocess.run(["git", "add", "."], shell=True)
        subprocess.run(["git", "commit", "-m", "Injected_New_Knowledge"], shell=True)
        subprocess.run(["git", "push", "origin", "main", "--force"], shell=True)
        print("[!] Injection Complete. Sniper is now smarter.")

if __name__ == "__main__":
    KnowledgeInjector().inject()