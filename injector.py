import os
import subprocess
import time

class SmartInjector:
    def __init__(self):
        self.kb_dir = "knowledge_base/reference_codes"
        os.makedirs(self.kb_dir, exist_ok=True)

    def is_repo_exists(self, repo_url):
        """Cek apakah folder repo sudah ada di lokal"""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_path = os.path.join(self.kb_dir, repo_name)
        return os.path.exists(target_path), target_path, repo_name

    def process_repo(self, repo_url):
        exists, target_path, repo_name = self.is_repo_exists(repo_url)
        
        if exists:
            print(f"[-] SKIPPED: {repo_name} sudah ada di database.")
            return False
        
        print(f"[*] NEW FOUND: Cloning {repo_name}...")
        # Clone hanya jika belum ada
        result = subprocess.run(["git", "clone", "--depth=1", repo_url, target_path], capture_output=True)
        
        if result.returncode == 0:
            # WAJIB: Hapus .git di dalam agar tidak jadi submodule/folder mati
            git_inner = os.path.join(target_path, ".git")
            if os.path.exists(git_inner):
                subprocess.run(f"rmdir /s /q \"{git_inner}\"", shell=True)
            
            # Bersihkan cache git utama agar folder baru terbaca sebagai file biasa
            subprocess.run(f"git rm -r --cached \"{target_path}\"", shell=True, capture_output=True)
            return True
        else:
            print(f"[!] Gagal cloning {repo_name}. Link mungkin salah.")
            return False

    def start(self):
        print("\n=== 🧠 KANA SMART INJECTOR ACTIVE ===")
        print("[*] Ketik 'exit' untuk berhenti.")
        
        while True:
            link = input("\n[?] Paste Link Repo/Hashtag: ").strip()
            
            if link.lower() == 'exit': break
            if not link: continue
            
            # Jika link tidak berakhiran .git, kita tambahkan
            if "github.com" in link and not link.endswith(".git"):
                link += ".git"

            if self.process_repo(link):
                print(f"[+] {link} Berhasil ditambahkan. Memulai Auto-Push...")
                
                # Eksekusi Git Push Otomatis
                subprocess.run("git add --all", shell=True)
                subprocess.run(f"git commit -m 'Added_New_Knowledge_{int(time.time())}'", shell=True)
                subprocess.run("git push origin main --force", shell=True)
                
                print("[!] UPDATE SUKSES: Data sudah masuk Cloud Kingkana22.")
            else:
                print("[!] Tidak ada perubahan yang perlu di-push.")

if __name__ == "__main__":
    SmartInjector().start()