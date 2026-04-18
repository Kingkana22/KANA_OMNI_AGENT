import re
import json
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, Request
from html.parser import HTMLParser

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


class ContentScraper:
    SUPPORTED_DOMAINS = {
        "github.com": "github",
        "raw.githubusercontent.com": "github_raw",
        "gist.github.com": "gist",
        "medium.com": "article",
        "dev.to": "article",
        "docs.github.com": "docs",
        "gitbook.io": "docs",
        "readthedocs.io": "docs",
        "stackoverflow.com": "qa",
        "reddit.com": "social",
        "hackernews.com": "social",
    }

    SUPPORTED_EXTENSIONS = {
        '.md', '.txt', '.json', '.py', '.sol', '.js', '.ts', '.php',
        '.html', '.yaml', '.yml', '.env', '.ini', '.xml', '.csv'
    }

    def __init__(self):
        self.repo_root = Path(__file__).resolve().parent
        self.kb_path = self.repo_root / "knowledge_base"
        self.scrape_dir = self.kb_path / "scraped_data"
        self.scrape_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.scrape_dir / "scrape_metadata.json"

    def load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def save_metadata(self, metadata):
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def detect_content_type(self, content):
        lines = content[:200].lower()
        if any(marker in lines for marker in ['```', '# ', '## ', '```python', '```solidity']):
            return "markdown"
        if content.strip().startswith(('{', '[')):
            return "json"
        if any(marker in lines for marker in ['<html', '<head', '<body', '<!doctype']):
            return "html"
        if any(marker in lines for marker in ['#!/', 'def ', 'class ', 'import ']):
            return "code"
        return "text"

    def detect_url_type(self, url):
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for known_domain, url_type in self.SUPPORTED_DOMAINS.items():
            if known_domain in domain:
                return url_type

        if any(ext in url.lower() for ext in ['.md', '.txt', '.json', '.py', '.sol']):
            return "file"
        if 'api.' in domain or 'raw.' in domain:
            return "api"
        return "webpage"

    def scrape_github_api(self, url):
        if not requests:
            return None, "[!] requests library tidak tersedia untuk GitHub scraping."

        if 'github.com/topics/' in url:
            return self.scrape_github_topic(url)
        elif 'gist.github.com' in url:
            return self.scrape_gist(url)
        elif 'raw.githubusercontent.com' in url:
            return self.scrape_raw_file(url)
        else:
            return self.scrape_github_repo(url)

    def scrape_github_repo(self, url):
        match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
        if not match:
            return None, f"[!] URL GitHub tidak valid: {url}"

        owner, repo = match.groups()
        repo = repo.replace('.git', '')
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        token = __import__('os').getenv("GITHUB_TOKEN")

        headers = {"Authorization": f"Bearer {token}"} if token else {}

        try:
            response = requests.get(api_url, headers=headers, timeout=20)
            if response.status_code != 200:
                return None, f"[!] GitHub API error {response.status_code}: {response.text}"

            repo_data = response.json()
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
            try:
                readme_resp = requests.get(readme_url, timeout=10)
                if readme_resp.status_code == 200:
                    readme_content = readme_resp.text
                else:
                    readme_content = ""
            except:
                readme_content = ""

            content = f"""# Repository: {repo_data.get('full_name')}

**URL**: {repo_data.get('html_url')}
**Description**: {repo_data.get('description', 'N/A')}
**Stars**: {repo_data.get('stargazers_count')}
**Language**: {repo_data.get('language', 'N/A')}
**Topics**: {', '.join(repo_data.get('topics', []))}

## README

{readme_content if readme_content else 'No README found.'}

---
_Scraped on {datetime.now().isoformat()}_
"""
            return content, None
        except Exception as e:
            return None, f"[!] Error scraping GitHub repo: {e}"

    def scrape_github_topic(self, url):
        match = re.search(r'github\.com/topics/([^/?]+)', url)
        if not match:
            return None, f"[!] URL topik GitHub tidak valid: {url}"

        topic = match.group(1)
        if not requests:
            return None, "[!] requests library tidak tersedia"

        api_url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&per_page=30"
        token = __import__('os').getenv("GITHUB_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        try:
            response = requests.get(api_url, headers=headers, timeout=20)
            if response.status_code != 200:
                return None, f"[!] GitHub API error: {response.status_code}"

            data = response.json()
            repos = data.get('items', [])
            content = f"# Topic: {topic}\n\nTop repositories tagged with '{topic}':\n\n"

            for repo in repos[:20]:
                content += f"- [{repo['full_name']}]({repo['html_url']}) - Stars: {repo['stargazers_count']}\n"
                content += f"  {repo.get('description', 'N/A')}\n\n"

            return content, None
        except Exception as e:
            return None, f"[!] Error scraping GitHub topic: {e}"

    def scrape_gist(self, url):
        if not requests:
            return None, "[!] requests library tidak tersedia"

        try:
            gist_id = url.split('/')[-1].split('#')[0]
            api_url = f"https://api.github.com/gists/{gist_id}"
            response = requests.get(api_url, timeout=10)

            if response.status_code != 200:
                return None, f"[!] Gist tidak ditemukan: {gist_id}"

            data = response.json()
            content = f"# Gist: {data.get('description', 'Untitled')}\n\n**URL**: {data.get('html_url')}\n\n"

            for filename, file_data in data.get('files', {}).items():
                content += f"## {filename}\n\n```\n{file_data.get('content', '')}\n```\n\n"

            return content, None
        except Exception as e:
            return None, f"[!] Error scraping gist: {e}"

    def scrape_raw_file(self, url):
        try:
            response = requests.get(url, timeout=20)
            if response.status_code != 200:
                return None, f"[!] File tidak ditemukan: {url}"
            return response.text, None
        except Exception as e:
            return None, f"[!] Error scraping raw file: {e}"

    def scrape_webpage(self, url):
        if not requests or not BeautifulSoup:
            return None, "[!] requests/BeautifulSoup library tidak tersedia"

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                return None, f"[!] Webpage tidak ditemukan: {response.status_code}"

            soup = BeautifulSoup(response.content, 'html.parser')

            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()

            title = soup.find('h1') or soup.find('title')
            title_text = title.get_text().strip() if title else "Untitled"

            content = f"# {title_text}\n\n"
            content += f"**Source**: {url}\n\n"

            for paragraph in soup.find_all(['p', 'article', 'main']):
                text = paragraph.get_text().strip()
                if text and len(text) > 10:
                    content += f"{text}\n\n"

            return content if len(content) > 50 else None, None
        except Exception as e:
            return None, f"[!] Error scraping webpage: {e}"

    def scrape_content(self, input_data):
        # Deteksi apakah input adalah URL atau paste content langsung
        input_data = input_data.strip()

        if input_data.startswith(('http://', 'https://', 'github.com', 'gist.github.com')):
            if not input_data.startswith(('http://', 'https://')):
                input_data = 'https://' + input_data

            url_type = self.detect_url_type(input_data)
            print(f"[*] Detected URL type: {url_type}")

            if url_type == "github":
                content, error = self.scrape_github_api(input_data)
            elif url_type == "gist":
                content, error = self.scrape_gist(input_data)
            elif url_type == "github_raw":
                content, error = self.scrape_raw_file(input_data)
            elif url_type in ["article", "docs", "webpage"]:
                content, error = self.scrape_webpage(input_data)
            else:
                content, error = self.scrape_raw_file(input_data)

            if error:
                return None, error
            return content, input_data
        else:
            # Treat as direct paste content
            return input_data, "pasted_content"

    def save_scraped_content(self, content, source):
        if not content:
            return None, "[!] Konten kosong, tidak dapat disimpan."

        timestamp = int(time.time())
        content_type = self.detect_content_type(content)
        ext = '.md' if content_type in ['markdown', 'text'] else '.json' if content_type == 'json' else '.txt'

        source_name = urlparse(source).netloc if source.startswith('http') else 'paste'
        source_name = source_name.replace('.', '_').replace(':', '_')

        filename = f"scraped_{source_name}_{timestamp}{ext}"
        filepath = self.scrape_dir / filename

        try:
            filepath.write_text(content, encoding='utf-8')
            metadata = self.load_metadata()
            metadata[filename] = {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "content_type": content_type,
                "size": len(content)
            }
            self.save_metadata(metadata)
            return filepath, None
        except Exception as e:
            return None, f"[!] Error saving content: {e}"

    def start_interactive(self):
        print("\n=== 📥 KANA CONTENT SCRAPER ===")
        print("[*] Paste URL, GitHub topic, atau konten langsung.")
        print("[*] Ketik 'exit' untuk berhenti.\n")

        while True:
            user_input = input("[?] Paste URL/Topik/Konten: ").strip()

            if user_input.lower() == 'exit':
                break
            if not user_input:
                continue

            print("[*] Scraping content...")
            content, source = self.scrape_content(user_input)

            if content is None:
                print(f"[!] {source}")
                continue

            print(f"[+] Content scraped successfully ({len(content)} chars)")
            save_choice = input("[?] Simpan ke knowledge_base? (y/n): ").strip().lower()

            if save_choice == 'y':
                filepath, error = self.save_scraped_content(content, source)
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"[+] Saved: {filepath}")


if __name__ == "__main__":
    scraper = ContentScraper()
    scraper.start_interactive()
