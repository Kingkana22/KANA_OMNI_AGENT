import re
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse


class SmartInjector:
    def __init__(self):
        self.repo_root = Path(__file__).resolve().parent
        self.kb_dir = self.repo_root / "knowledge_base" / "reference_codes"
        self.kb_dir.mkdir(parents=True, exist_ok=True)

    def normalize_repo_url(self, repo_url):
        repo_url = repo_url.strip()
        if repo_url.startswith("github.com"):
            repo_url = "https://" + repo_url

        if "github.com" in repo_url and not repo_url.endswith(".git"):
            repo_url += ".git"

        return repo_url

    def repo_name_from_url(self, repo_url):
        parsed = urlparse(repo_url)
        repo_name = Path(parsed.path).stem
        return repo_name or None

    def is_repo_exists(self, repo_url):
        repo_url = self.normalize_repo_url(repo_url)
        repo_name = self.repo_name_from_url(repo_url)
        target_path = self.kb_dir / repo_name
        return target_path.exists(), target_path, repo_name

    def process_repo(self, repo_url):
        repo_url = self.normalize_repo_url(repo_url)
        exists, target_path, repo_name = self.is_repo_exists(repo_url)

        if not repo_name:
            print(f"[!] URL tidak valid: {repo_url}")
            return None

        if exists:
            print(f"[-] SKIPPED: {repo_name} sudah ada di database.")
            return None

        print(f"[*] NEW FOUND: Cloning {repo_name}...")
        result = subprocess.run(
            ["git", "clone", "--depth=1", repo_url, str(target_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"[!] Gagal cloning {repo_name}: {result.stderr.strip()}")
            return None

        git_dir = target_path / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir, ignore_errors=True)

        print(f"[+] Repo {repo_name} berhasil dikloning ke {target_path}.")
        return target_path

    def current_branch(self):
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "main"

    def has_git_changes(self, target_path):
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(target_path)],
            capture_output=True,
            text=True,
        )
        return bool(result.stdout.strip())

    def commit_and_push(self, target_path):
        subprocess.run(["git", "add", "--", str(target_path)], capture_output=True, text=True)

        if not self.has_git_changes(target_path):
            print("[!] Tidak ada perubahan yang perlu di-commit.")
            return False

        branch = self.current_branch()
        commit_message = f"Added_New_Knowledge_{target_path.name}_{int(time.time())}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"[!] Commit gagal: {result.stderr.strip()}")
            return False

        push = subprocess.run(
            ["git", "push", "origin", branch],
            capture_output=True,
            text=True,
        )

        if push.returncode != 0:
            print(f"[!] Push gagal: {push.stderr.strip()}")
            return False

        return True

    def start(self):
        print("\n=== 🧠 KANA SMART INJECTOR ACTIVE ===")
        print("[*] Ketik 'exit' untuk berhenti.")

        while True:
            link = input("\n[?] Paste Link Repo/Hashtag: ").strip()
            if link.lower() == 'exit':
                break
            if not link:
                continue

            if "github.com" in link and not link.endswith(".git"):
                link += ".git"

            target_path = self.process_repo(link)
            if target_path:
                print(f"[+] {link} berhasil ditambahkan. Memulai Auto-Push...")
                if self.commit_and_push(target_path):
                    print("[!] UPDATE SUKSES: Data sudah masuk Cloud Kingkana22.")
                else:
                    print("[!] Commit/push gagal. Periksa status git Anda.")
            else:
                print("[!] Tidak ada perubahan yang perlu di-push atau proses gagal.")


if __name__ == "__main__":
    SmartInjector().start()