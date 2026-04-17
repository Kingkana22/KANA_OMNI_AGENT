#!/usr/bin/env python
"""
KANA OMNI - SINGLE FILE EDITION
All tools consolidated into one file for easier management
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
import subprocess
import threading

# Optional imports with fallbacks
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    requests = None
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    BeautifulSoup = None
    HAS_BS4 = False


# ================================
# SHARED UTILITIES
# ================================

class KanaUtils:
    """Shared utilities for all tools"""

    @staticmethod
    def ensure_dir(path):
        """Ensure directory exists"""
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_json(file_path, default=None):
        """Load JSON file safely"""
        if default is None:
            default = {}
        try:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return default

    @staticmethod
    def save_json(file_path, data):
        """Save JSON file safely"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except:
            return False

    @staticmethod
    def run_command(cmd, cwd=None, capture_output=True):
        """Run shell command safely"""
        try:
            result = subprocess.run(
                cmd if isinstance(cmd, list) else cmd.split(),
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except:
            return False, "", "Command failed"


# ================================
# TOOL CLASSES
# ================================

class SmartInjector:
    """Repository injection tool"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.reference_codes = self.root / "knowledge_base" / "reference_codes"
        KanaUtils.ensure_dir(self.reference_codes)

    def process_repo(self, repo_url):
        """Clone and process repository"""
        if not repo_url:
            return None

        # Extract repo name
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        target_path = self.reference_codes / repo_name

        if target_path.exists():
            print(f"[!] Repository {repo_name} already exists")
            return str(target_path)

        print(f"[*] Cloning {repo_url}...")

        success, stdout, stderr = KanaUtils.run_command(
            ["git", "clone", repo_url, str(target_path)]
        )

        if success:
            # Remove .git directory
            git_dir = target_path / ".git"
            if git_dir.exists():
                import shutil
                shutil.rmtree(git_dir)

            print(f"[+] Repository cloned: {target_path}")
            return str(target_path)
        else:
            print(f"[!] Clone failed: {stderr}")
            return None

    def commit_and_push(self, repo_path):
        """Commit and push changes"""
        # This would need git credentials setup
        return False


class ContentScraper:
    """Content scraping tool"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.kb_path = self.root / "knowledge_base"
        self.scrape_dir = self.kb_path / "scraped_data"
        KanaUtils.ensure_dir(self.scrape_dir)

    def scrape_content(self, input_text):
        """Scrape content from various sources"""
        if not input_text:
            return None, "No input provided"

        # Simple content extraction (placeholder)
        if input_text.startswith('http'):
            if HAS_REQUESTS:
                try:
                    response = requests.get(input_text, timeout=10)
                    if response.status_code == 200:
                        return response.text, f"webpage:{input_text}"
                except:
                    pass
            return None, "Failed to fetch webpage (requests not available)"

        # Direct content
        return input_text, "direct_content"

    def save_scraped_content(self, content, source):
        """Save scraped content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraped_{source.replace('/', '_').replace(':', '_')}_{timestamp}.md"
        filepath = self.scrape_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Scraped Content\n\n**Source:** {source}\n**Date:** {datetime.now().isoformat()}\n\n{content}")
            return str(filepath), None
        except Exception as e:
            return None, str(e)


class KanaHunter:
    """Pattern hunting tool"""

    def __init__(self, niche=None):
        self.niche = niche
        self.root = Path(__file__).resolve().parent
        self.kb_path = self.root / "knowledge_base"

    def hunt_github(self):
        """Search GitHub for patterns"""
        print("[*] GitHub hunting not implemented in single-file version")
        print("[*] Use web scraping or API calls for real implementation")


class Web3GasFinder:
    """Gas price monitoring tool"""

    GAS_APIS = {
        "eth": {
            "name": "Ethereum",
            "api_url": "https://api.etherscan.io/api",
            "param_key": "module=gastracker&action=gasoracle",
            "unit": "Gwei"
        }
    }

    def get_current_gas_price(self, chain="eth"):
        """Get current gas price"""
        if not HAS_REQUESTS:
            return None, "[!] requests library not available"

        chain_info = self.GAS_APIS.get(chain)
        if not chain_info:
            return None, f"[!] Chain {chain} not supported"

        try:
            url = f"{chain_info['api_url']}?{chain_info['param_key']}&apikey="
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("status") == "1":
                result = data.get("result", {})
                gas_info = {
                    "chain": chain,
                    "timestamp": datetime.now().isoformat(),
                    "safe_gas_price": float(result.get("SafeGasPrice", 0)),
                    "standard_gas_price": float(result.get("ProposeGasPrice", 0)),
                    "fast_gas_price": float(result.get("FastGasPrice", 0)),
                    "unit": chain_info["unit"]
                }
                return gas_info, None
            else:
                return None, "[!] Unable to fetch gas price"
        except Exception as e:
            return None, f"[!] Error: {e}"

    def find_cheapest_chain(self):
        """Find cheapest gas across chains"""
        print("[*] Scanning gas prices...")

        gas_info, error = self.get_current_gas_price("eth")
        if error:
            print(f"[!] {error}")
            return None

        print(f"[+] ETH: {gas_info['standard_gas_price']} Gwei")
        return gas_info

    def interactive_gas_finder(self):
        """Interactive gas finder"""
        print("\n=== 💰 WEB3 GAS FINDER (Single-File) ===")

        while True:
            print("[1] Check gas prices")
            print("[2] Find cheapest chain")
            print("[0] Exit")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                gas_info, error = self.get_current_gas_price("eth")
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"[+] ETH Gas: {gas_info['standard_gas_price']} Gwei")

            elif choice == '2':
                self.find_cheapest_chain()

            elif choice == '0':
                break


class KanaWalletManager:
    """Wallet management tool"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.wallet_dir = self.root / "knowledge_base" / "wallets"
        KanaUtils.ensure_dir(self.wallet_dir)

        self.personal_wallet_file = self.wallet_dir / "personal_wallet.json"
        self.bank_file = self.wallet_dir / "bank_accounts.json"

        self.load_wallets()

    def load_wallets(self):
        """Load wallet data"""
        self.personal_wallet = KanaUtils.load_json(self.personal_wallet_file, {
            "address": "",
            "balance": 0,
            "chain": "eth",
            "created": datetime.now().isoformat(),
            "transactions": []
        })

        self.bank_accounts = KanaUtils.load_json(self.bank_file, {})

    def save_wallets(self):
        """Save wallet data"""
        KanaUtils.save_json(self.personal_wallet_file, self.personal_wallet)
        KanaUtils.save_json(self.bank_file, self.bank_accounts)

    def set_personal_wallet(self, address, chain="eth"):
        """Set personal wallet"""
        self.personal_wallet["address"] = address
        self.personal_wallet["chain"] = chain
        self.save_wallets()
        print(f"[+] Personal wallet set: {address}")

    def add_bank_account(self, name, address, chain="eth"):
        """Add death wallet to bank"""
        wallet_id = hashlib.md5(f"{name}{address}{chain}".encode()).hexdigest()[:8]

        self.bank_accounts[wallet_id] = {
            "name": name,
            "address": address,
            "chain": chain,
            "added": datetime.now().isoformat(),
            "balance": 0,
            "coding_efforts": 0,
            "transactions": []
        }

        self.save_wallets()
        print(f"[+] Bank account added: {name} ({wallet_id})")
        return wallet_id

    def list_bank_accounts(self):
        """List bank accounts"""
        if not self.bank_accounts:
            print("[!] No bank accounts")
            return

        print(f"\n=== 💰 KANA BANK ({len(self.bank_accounts)} accounts) ===")
        for wallet_id, account in self.bank_accounts.items():
            print(f"[{wallet_id}] {account['name']}: {account['coding_efforts']} points")

    def interactive_wallet_manager(self):
        """Interactive wallet manager"""
        print("\n=== 💳 KANA WALLET MANAGER ===")

        while True:
            print("[1] Set personal wallet")
            print("[2] Add bank account")
            print("[3] List bank accounts")
            print("[0] Exit")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                self.set_personal_wallet(address, chain)

            elif choice == '2':
                name = input("[?] Account name: ").strip()
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain: ").strip() or "eth"
                self.add_bank_account(name, address, chain)

            elif choice == '3':
                self.list_bank_accounts()

            elif choice == '0':
                break


# ================================
# MAIN ORCHESTRATOR
# ================================

class KanaOmniSingleFile:
    """Single-file orchestrator for all tools"""

    def __init__(self):
        # Initialize all tools
        self.injector = SmartInjector()
        self.scraper = ContentScraper()
        self.hunter = KanaHunter()
        self.gas_finder = Web3GasFinder()
        self.wallet_manager = KanaWalletManager()

        # Tools that require external deps
        self.reaper = None  # Requires requests
        self.immunefi_worker = None  # Requires requests + bs4

        # Check optional tools
        if HAS_REQUESTS:
            print("[+] Reaper Bot available (has requests)")
            # Could initialize reaper here
        else:
            print("[-] Reaper Bot unavailable (missing requests)")

        if HAS_REQUESTS and HAS_BS4:
            print("[+] Immunefi Worker available")
        else:
            print("[-] Immunefi Worker unavailable (missing requests/bs4)")

    def show_menu(self):
        print("\n" + "=" * 60)
        print("   🧠 KANA OMNI - SINGLE FILE EDITION")
        print("=" * 60)
        print("\n[1] 📦 Smart Injector - Clone repositories")
        print("[2] 📥 Content Scraper - Extract content")
        print("[3] 🎯 Dork Hunter - Pattern search")
        print("[4] 💰 Web3 Gas Finder - Gas prices")
        print("[5] 💳 Wallet Manager - Personal & bank wallets")
        print("[6] 📋 Tool Status - Available tools")
        print("[0] 🚪 Exit\n")

    def menu_inject(self):
        print("\n=== 📦 REPOSITORY INJECTOR ===")

        while True:
            link = input("[?] GitHub Repo URL (or 'exit'): ").strip()
            if link.lower() == 'exit':
                break

            if "github.com" in link and not link.endswith(".git"):
                link += ".git"

            target_path = self.injector.process_repo(link)
            if target_path:
                print(f"[+] Repository added: {target_path}")

    def menu_scrape(self):
        print("\n=== 📥 CONTENT SCRAPER ===")

        while True:
            user_input = input("[?] URL/Content (or 'exit'): ").strip()
            if user_input.lower() == 'exit':
                break

            content, source = self.scraper.scrape_content(user_input)
            if content:
                filepath, error = self.scraper.save_scraped_content(content, source)
                if filepath:
                    print(f"[+] Saved: {filepath}")
                else:
                    print(f"[!] Save failed: {error}")
            else:
                print(f"[!] {source}")

    def menu_gas_finder(self):
        self.gas_finder.interactive_gas_finder()

    def menu_wallet_manager(self):
        self.wallet_manager.interactive_wallet_manager()

    def menu_tool_status(self):
        print("\n=== 📋 TOOL STATUS ===")
        print("✅ Smart Injector - Always available")
        print("✅ Content Scraper - Always available")
        print("✅ Dork Hunter - Always available")
        print("✅ Web3 Gas Finder - Always available")
        print("✅ Wallet Manager - Always available")

        if HAS_REQUESTS:
            print("✅ Reaper Bot - Available (has requests)")
        else:
            print("❌ Reaper Bot - Missing requests")

        if HAS_REQUESTS and HAS_BS4:
            print("✅ Immunefi Worker - Available")
        else:
            print("❌ Immunefi Worker - Missing requests/bs4")

    def run(self):
        while True:
            self.show_menu()
            choice = input("[?] Select action: ").strip()

            if choice == '1':
                self.menu_inject()
            elif choice == '2':
                self.menu_scrape()
            elif choice == '3':
                self.hunter.hunt_github()
            elif choice == '4':
                self.menu_gas_finder()
            elif choice == '5':
                self.menu_wallet_manager()
            elif choice == '6':
                self.menu_tool_status()
            elif choice == '0':
                print("\n[!] Goodbye! 🧠\n")
                break
            else:
                print("[!] Invalid choice.")


# ================================
# MAIN EXECUTION
# ================================

if __name__ == "__main__":
    print("🧠 KANA OMNI - Single File Edition")
    print(f"Dependencies: requests={HAS_REQUESTS}, bs4={HAS_BS4}")

    try:
        orchestrator = KanaOmniSingleFile()
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()