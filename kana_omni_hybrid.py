#!/usr/bin/env python
"""
KANA OMNI - HYBRID EDITION
Core tools in main file + plugin system for extensibility
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
import importlib.util

# Optional imports
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
# CORE UTILITIES
# ================================

class KanaCore:
    """Core utilities and shared functionality"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.kb_path = self.root / "knowledge_base"
        self.ensure_dirs()

    def ensure_dirs(self):
        """Ensure all required directories exist"""
        dirs = [
            self.kb_path,
            self.kb_path / "reference_codes",
            self.kb_path / "scraped_data",
            self.kb_path / "wallets",
            self.kb_path / "immunefi_bounties",
            self.kb_path / "immunefi_bounties" / "pocs"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_json(file_path, default=None):
        """Load JSON safely"""
        if default is None:
            default = {}
        try:
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default

    @staticmethod
    def save_json(file_path, data):
        """Save JSON safely"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False

    @staticmethod
    def run_command(cmd, cwd=None, timeout=30):
        """Run shell command safely"""
        try:
            result = subprocess.run(
                cmd if isinstance(cmd, list) else cmd.split(),
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except:
            return False, "", "Command failed"


# ================================
# CORE TOOLS (Always Available)
# ================================

class SmartInjector(KanaCore):
    """Repository injection tool"""

    def __init__(self):
        super().__init__()
        self.reference_codes = self.kb_path / "reference_codes"

    def process_repo(self, repo_url):
        """Clone and process repository"""
        if not repo_url:
            return None

        repo_name = repo_url.split('/')[-1].replace('.git', '')
        target_path = self.reference_codes / repo_name

        if target_path.exists():
            print(f"[!] Repository {repo_name} already exists")
            return str(target_path)

        print(f"[*] Cloning {repo_url}...")

        success, stdout, stderr = self.run_command(
            ["git", "clone", "--depth", "1", repo_url, str(target_path)]
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


class ContentScraper(KanaCore):
    """Content scraping tool"""

    def __init__(self):
        super().__init__()
        self.scrape_dir = self.kb_path / "scraped_data"

    def scrape_content(self, input_text):
        """Scrape content from various sources"""
        if not input_text:
            return None, "No input provided"

        # GitHub repo
        if "github.com" in input_text and "/tree/" not in input_text:
            return self._scrape_github_repo(input_text)

        # Direct content
        return input_text, "direct_content"

    def _scrape_github_repo(self, repo_url):
        """Scrape GitHub repository"""
        if not HAS_REQUESTS:
            return None, "requests library required for GitHub scraping"

        try:
            # Convert to API URL
            if "github.com" in repo_url:
                api_url = repo_url.replace("github.com", "api.github.com/repos")
                if api_url.endswith(".git"):
                    api_url = api_url[:-4]

            headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN', '')}"}
            response = requests.get(f"{api_url}/readme", headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                if content:
                    import base64
                    content = base64.b64decode(content).decode('utf-8')
                    return content, f"github:{repo_url}"

        except Exception as e:
            return None, f"GitHub scrape failed: {e}"

        return None, "Failed to scrape GitHub repo"

    def save_scraped_content(self, content, source):
        """Save scraped content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_source = source.replace('/', '_').replace(':', '_').replace('@', '_')
        filename = f"scraped_{safe_source}_{timestamp}.md"
        filepath = self.scrape_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Scraped Content\n\n**Source:** {source}\n**Date:** {datetime.now().isoformat()}\n\n{content}")
            return str(filepath), None
        except Exception as e:
            return None, str(e)


class KanaWalletManager(KanaCore):
    """Wallet management system"""

    def __init__(self):
        super().__init__()
        self.wallet_dir = self.kb_path / "wallets"
        self.personal_wallet_file = self.wallet_dir / "personal_wallet.json"
        self.bank_file = self.wallet_dir / "bank_accounts.json"
        self.load_wallets()

    def load_wallets(self):
        """Load wallet data"""
        self.personal_wallet = self.load_json(self.personal_wallet_file, {
            "address": "",
            "balance": 0,
            "chain": "eth",
            "created": datetime.now().isoformat(),
            "transactions": []
        })
        self.bank_accounts = self.load_json(self.bank_file, {})

    def save_wallets(self):
        """Save wallet data"""
        self.save_json(self.personal_wallet_file, self.personal_wallet)
        self.save_json(self.bank_file, self.bank_accounts)

    def set_personal_wallet(self, address, chain="eth"):
        """Set personal wallet"""
        self.personal_wallet.update({
            "address": address,
            "chain": chain,
            "updated": datetime.now().isoformat()
        })
        self.save_wallets()
        print(f"[+] Personal wallet set: {address} ({chain})")

    def add_bank_account(self, name, address, chain="eth", source="manual"):
        """Add death wallet to bank"""
        wallet_id = hashlib.md5(f"{name}{address}{chain}".encode()).hexdigest()[:8]

        self.bank_accounts[wallet_id] = {
            "name": name,
            "address": address,
            "chain": chain,
            "source": source,
            "added": datetime.now().isoformat(),
            "balance": 0,
            "coding_efforts": 0,
            "transactions": []
        }

        self.save_wallets()
        print(f"[+] Bank account added: {name} ({wallet_id})")
        return wallet_id

    def earn_coding_points(self, wallet_id, points, reason="coding_task"):
        """Earn points from coding efforts"""
        if wallet_id in self.bank_accounts:
            account = self.bank_accounts[wallet_id]
            account["coding_efforts"] += points
            account["transactions"].append({
                "type": "earn",
                "points": points,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            self.save_wallets()
            print(f"[+] Earned {points} points for {wallet_id}")

    def list_bank_accounts(self):
        """List all bank accounts"""
        if not self.bank_accounts:
            print("[!] No bank accounts found")
            return

        print(f"\n=== 💰 KANA BANK ACCOUNTS ({len(self.bank_accounts)}) ===")
        for wallet_id, account in self.bank_accounts.items():
            print(f"[{wallet_id}] {account['name']}")
            print(f"   Address: {account['address']} ({account['chain']})")
            print(f"   Balance: {account['coding_efforts']} points")
            print(f"   Source: {account['source']}\n")


# ================================
# PLUGIN SYSTEM
# ================================

class KanaPluginSystem:
    """Plugin system for loading optional tools"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.plugins = {}
        self.loaded_plugins = {}
        self.discover_plugins()

    def discover_plugins(self):
        """Discover available plugins"""
        # Core plugins (separate files)
        core_plugins = {
            "reaper": {
                "module": "agent",
                "class": "KanaOmniReaper",
                "description": "BSC contract monitor",
                "requires": ["requests"]
            },
            "immunefi": {
                "module": "immunefi_worker",
                "class": "ImmunefiWorker",
                "description": "Bug bounty automation",
                "requires": ["requests", "bs4"]
            },
            "whitehat": {
                "module": "whitehat_worker",
                "class": "WhiteHatWorker",
                "description": "Auto-scan dead addresses",
                "requires": ["requests"]
            },
            "gas_finder": {
                "module": "web3_gas_finder",
                "class": "Web3GasFinder",
                "description": "Gas price monitoring",
                "requires": []
            }
        }

        for plugin_name, plugin_info in core_plugins.items():
            self.plugins[plugin_name] = plugin_info
            self.plugins[plugin_name]["available"] = self._check_plugin_requirements(plugin_info)

    def _check_plugin_requirements(self, plugin_info):
        """Check if plugin requirements are met"""
        for req in plugin_info["requires"]:
            if req == "requests" and not HAS_REQUESTS:
                return False
            if req == "bs4" and not HAS_BS4:
                return False
        return True

    def load_plugin(self, plugin_name):
        """Load a plugin dynamically"""
        if plugin_name not in self.plugins:
            return None, f"Plugin {plugin_name} not found"

        plugin_info = self.plugins[plugin_name]
        if not plugin_info["available"]:
            return None, f"Plugin {plugin_name} requirements not met"

        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name], None

        try:
            module = __import__(plugin_info["module"])
            plugin_class = getattr(module, plugin_info["class"])
            plugin_instance = plugin_class()

            self.loaded_plugins[plugin_name] = plugin_instance
            return plugin_instance, None

        except Exception as e:
            return None, f"Failed to load plugin {plugin_name}: {e}"

    def get_available_plugins(self):
        """Get list of available plugins"""
        return {k: v for k, v in self.plugins.items() if v["available"]}

    def get_plugin_status(self):
        """Get status of all plugins"""
        status = {}
        for name, info in self.plugins.items():
            status[name] = {
                "available": info["available"],
                "description": info["description"],
                "loaded": name in self.loaded_plugins
            }
        return status


# ================================
# HYBRID ORCHESTRATOR
# ================================

class KanaOmniHybrid:
    """Hybrid orchestrator with core tools + plugin system"""

    def __init__(self):
        # Core tools (always available)
        self.injector = SmartInjector()
        self.scraper = ContentScraper()
        self.wallet_manager = KanaWalletManager()

        # Plugin system
        self.plugin_system = KanaPluginSystem()

        # Lazy-loaded plugins
        self._reaper = None
        self._gas_finder = None
        self._whitehat = None
        self._immunefi = None

    @property
    def reaper(self):
        """Lazy load reaper plugin"""
        if self._reaper is None:
            self._reaper, _ = self.plugin_system.load_plugin("reaper")
        return self._reaper

    @property
    def gas_finder(self):
        """Lazy load gas finder plugin"""
        if self._gas_finder is None:
            self._gas_finder, _ = self.plugin_system.load_plugin("gas_finder")
        return self._gas_finder

    @property
    def whitehat_worker(self):
        """Lazy load whitehat worker plugin"""
        if self._whitehat is None:
            self._whitehat, _ = self.plugin_system.load_plugin("whitehat")
        return self._whitehat

    @property
    def immunefi_worker(self):
        """Lazy load immunefi worker plugin"""
        if self._immunefi is None:
            self._immunefi, _ = self.plugin_system.load_plugin("immunefi")
        return self._immunefi

    def show_menu(self):
        print("\n" + "=" * 60)
        print("   🧠 KANA OMNI - HYBRID EDITION")
        print("=" * 60)
        print("\n[1] 📦 Smart Injector - Clone repositories")
        print("[2] 📥 Content Scraper - Extract content")
        print("[3] 💳 Wallet Manager - Personal & bank wallets")
        print("[4] 💰 Gas Finder - Gas prices & claiming")
        print("[5] 🤖 Reaper Bot - Contract monitoring")
        print("[6] 🛡️ White Hat Worker - Dead address scanner")
        print("[7] 🐛 Immunefi Worker - Bug bounty automation")
        print("[8] 📋 Tool Status - Available tools")
        print("[9] 🔧 Plugin Manager - Manage plugins")
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

    def menu_wallet_manager(self):
        print("\n=== 💳 KANA WALLET MANAGER ===")

        while True:
            print("[1] Set personal wallet")
            print("[2] Add bank account")
            print("[3] List bank accounts")
            print("[4] Earn coding points")
            print("[0] Exit")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                self.wallet_manager.set_personal_wallet(address, chain)

            elif choice == '2':
                name = input("[?] Account name: ").strip()
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain: ").strip() or "eth"
                source = input("[?] Source: ").strip() or "manual"
                self.wallet_manager.add_bank_account(name, address, chain, source)

            elif choice == '3':
                self.wallet_manager.list_bank_accounts()

            elif choice == '4':
                self.wallet_manager.list_bank_accounts()
                wallet_id = input("[?] Select wallet ID: ").strip()
                points = int(input("[?] Points to earn: ").strip() or "10")
                reason = input("[?] Reason: ").strip() or "coding_task"
                self.wallet_manager.earn_coding_points(wallet_id, points, reason)

            elif choice == '0':
                break

    def menu_gas_finder(self):
        if not self.gas_finder:
            print("[!] Gas Finder plugin not available")
            return

        print("\n=== 💰 WEB3 GAS FINDER ===")

        while True:
            print("[1] Check gas prices")
            print("[2] Find cheapest chain")
            print("[3] Claim free gas")
            print("[0] Exit")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                gas_info, error = self.gas_finder.get_current_gas_price("eth")
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"[+] ETH Gas: {gas_info['standard_gas_price']} Gwei")

            elif choice == '2':
                result = self.gas_finder.find_cheapest_chain()
                if result:
                    print(f"[+] Cheapest: {result['chain'].upper()}")

            elif choice == '3':
                wallet = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                success, message = self.gas_finder.claim_free_gas(chain, wallet)
                if success:
                    print("[+] Gas claimed successfully!")
                else:
                    print(f"[!] {message}")

            elif choice == '0':
                break

    def menu_reaper(self):
        if not self.reaper:
            print("[!] Reaper Bot plugin not available")
            return

        print("[*] Reaper Bot would start monitoring here...")
        print("[*] (Full implementation in separate plugin file)")

    def menu_whitehat(self):
        if not self.whitehat_worker:
            print("[!] White Hat Worker plugin not available")
            return

        print("[*] White Hat Worker would scan for dead addresses here...")
        print("[*] (Full implementation in separate plugin file)")

    def menu_immunefi(self):
        if not self.immunefi_worker:
            print("[!] Immunefi Worker plugin not available")
            return

        print("[*] Immunefi Worker would hunt bounties here...")
        print("[*] (Full implementation in separate plugin file)")

    def menu_tool_status(self):
        print("\n=== 📋 TOOL STATUS ===")
        print("✅ Smart Injector - Core tool (always available)")
        print("✅ Content Scraper - Core tool (always available)")
        print("✅ Wallet Manager - Core tool (always available)")

        plugin_status = self.plugin_system.get_plugin_status()
        for plugin_name, status in plugin_status.items():
            icon = "✅" if status["available"] else "❌"
            loaded = " (loaded)" if status["loaded"] else ""
            print(f"{icon} {plugin_name.title()} - {status['description']}{loaded}")

    def menu_plugin_manager(self):
        print("\n=== 🔧 PLUGIN MANAGER ===")

        while True:
            print("[1] List available plugins")
            print("[2] Load plugin")
            print("[3] Check plugin status")
            print("[0] Exit")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                available = self.plugin_system.get_available_plugins()
                if available:
                    print(f"\n[+] Available plugins ({len(available)}):")
                    for name, info in available.items():
                        print(f"  • {name}: {info['description']}")
                else:
                    print("[!] No plugins available")

            elif choice == '2':
                available = self.plugin_system.get_available_plugins()
                if available:
                    print(f"\nAvailable plugins:")
                    for i, (name, info) in enumerate(available.items(), 1):
                        print(f"[{i}] {name}: {info['description']}")

                    try:
                        idx = int(input("[?] Select plugin number: ").strip()) - 1
                        plugin_name = list(available.keys())[idx]
                        plugin, error = self.plugin_system.load_plugin(plugin_name)
                        if plugin:
                            print(f"[+] Plugin {plugin_name} loaded successfully")
                        else:
                            print(f"[!] Failed to load {plugin_name}: {error}")
                    except (ValueError, IndexError):
                        print("[!] Invalid selection")
                else:
                    print("[!] No plugins available")

            elif choice == '3':
                status = self.plugin_system.get_plugin_status()
                print(f"\nPlugin Status ({len(status)} total):")
                for name, info in status.items():
                    avail = "✅ Available" if info["available"] else "❌ Unavailable"
                    loaded = " (loaded)" if info["loaded"] else ""
                    print(f"  {name}: {avail}{loaded}")

            elif choice == '0':
                break

    def run(self):
        print(f"🧠 KANA OMNI Hybrid Edition")
        print(f"Core tools: ✅ Always available")
        print(f"Plugins: {len(self.plugin_system.get_available_plugins())} available")

        while True:
            self.show_menu()
            choice = input("[?] Select action: ").strip()

            if choice == '1':
                self.menu_inject()
            elif choice == '2':
                self.menu_scrape()
            elif choice == '3':
                self.menu_wallet_manager()
            elif choice == '4':
                self.menu_gas_finder()
            elif choice == '5':
                self.menu_reaper()
            elif choice == '6':
                self.menu_whitehat()
            elif choice == '7':
                self.menu_immunefi()
            elif choice == '8':
                self.menu_tool_status()
            elif choice == '9':
                self.menu_plugin_manager()
            elif choice == '0':
                print("\n[!] Goodbye! 🧠\n")
                break
            else:
                print("[!] Invalid choice.")


# ================================
# MAIN EXECUTION
# ================================

if __name__ == "__main__":
    try:
        orchestrator = KanaOmniHybrid()
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()