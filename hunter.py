import os
import re
import time
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

try:
    from notifier import send_kana_alert
except ImportError:
    def send_kana_alert(message):
        print(message)


class KanaHunter:
    DEFAULT_DORKS = [
        "filename:.env DB_PASSWORD",
        "extension:sol 'selfdestruct'",
        "extension:sol 'delegatecall'",
        "filename:config.php password",
        "path:knowledge_base vulnerability"
    ]

    NICHE_MAP = {
        "web3": [
            "extension:sol reentrancy",
            "extension:sol delegatecall",
            "extension:sol selfdestruct",
            "language:Solidity 'unchecked' transfer",
            "extension:sol 'require('"
        ],
        "bugbounty": [
            "filename:.env password",
            "extension:php 'password'",
            "extension:js 'apiKey'",
            "filename:config.php 'DB_PASSWORD'",
            "path:secret token"
        ],
        "infosec": [
            "filename:.env DB_PASSWORD",
            "filename:config.php password",
            "extension:php 'eval('",
            "extension:js 'document.cookie'",
            "extension:yaml secret"
        ]
    }

    SUPPORTED_EXTENSIONS = {'.md', '.sol', '.json', '.txt', '.yaml', '.yml', '.py', '.js', '.ts', '.php', '.env', '.ini'}

    def __init__(self, niche=None):
        self.repo_root = Path(__file__).resolve().parent
        self.kb_path = self.repo_root / "knowledge_base"
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.niche = niche and niche.strip().lower()
        self.dorks = self.build_dorks()

    def build_dorks(self):
        dorks = self.DEFAULT_DORKS.copy()
        if self.niche and self.niche in self.NICHE_MAP:
            dorks.extend(self.NICHE_MAP[self.niche])
        return dorks

    def hunt_github(self):
        print("\n" + "=" * 40)
        print("   KANA CORE: HUNTER MODE ACTIVE")
        print("=" * 40)

        if self.github_token and requests:
            print("[*] GitHub token detected. Running live GitHub code search.")
            for query in self.dorks:
                print(f"[*] Searching GitHub for: {query}")
                self.search_github_code(query)
                time.sleep(2)
        else:
            reason = "no GitHub token" if not self.github_token else "requests library missing"
            print(f"[*] Falling back to local knowledge_base audit because {reason}.")
            for query in self.dorks:
                print(f"[*] Auditing local knowledge_base for: {query}")
                self.internal_audit(query)
                time.sleep(1)

    def search_github_code(self, query):
        if not requests:
            print("[!] requests library is not installed. Cannot perform GitHub search.")
            return

        url = "https://api.github.com/search/code"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.github_token}"
        }
        params = {"q": query, "per_page": 10}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
        except Exception as e:
            print(f"[!] GitHub search failed: {e}")
            return

        if response.status_code != 200:
            print(f"[!] GitHub API error {response.status_code}: {response.text.strip()}")
            return

        data = response.json()
        items = data.get("items", [])
        if not items:
            print("[ ] No live GitHub matches found.")
            return

        for item in items:
            path = item.get("path")
            repo_name = item.get("repository", {}).get("full_name")
            msg = f"🎯 GitHub match: {repo_name}/{path}\nPattern: {query}\nURL: {item.get('html_url')}"
            print(msg)
            send_kana_alert(msg)

    def internal_audit(self, query):
        if not self.kb_path.exists():
            print(f"[!] knowledge_base path not found: {self.kb_path}")
            return

        filters, terms = self.parse_dork(query)
        matches = []

        for path in self.kb_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            if not self.matches_file_filters(path, filters):
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                print(f"[!] Tidak bisa membaca {path}: {e}")
                continue

            content_lower = content.lower()
            if all(term.lower() in content_lower for term in terms):
                matches.append(path)
                msg = f"🎯 TARGET IDENTIFIED: {path.relative_to(self.repo_root)}\nPattern: {query}\nStatus: Ready for Audit."
                print(msg)
                send_kana_alert(msg)

        if not matches:
            print("[ ] Tidak ditemukan target di knowledge_base untuk pola ini.")

    def parse_dork(self, query):
        filters = {}
        terms = []
        for token in query.split():
            if ":" in token:
                key, value = token.split(":", 1)
                if key in {"filename", "extension", "path", "repo", "language"}:
                    filters[key] = value.strip("'\"")
                    continue
            terms.append(token.strip("'\""))
        return filters, [term for term in terms if term]

    def matches_file_filters(self, path, filters):
        if not filters:
            return True

        file_name = path.name.lower()
        file_path = str(path).lower()
        extension = path.suffix.lower().lstrip(".")

        if "filename" in filters and filters["filename"].lower() not in file_name:
            return False
        if "extension" in filters and filters["extension"].lower().lstrip(".") != extension:
            return False
        if "path" in filters and filters["path"].lower() not in file_path:
            return False
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run KanaHunter dork search against knowledge_base or GitHub.")
    parser.add_argument("--niche", help="Choose a niche to extend dork search (web3, bugbounty, infosec)")
    args = parser.parse_args()

    hunter = KanaHunter(niche=args.niche)
    hunter.hunt_github()