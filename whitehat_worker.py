import os
import re
import json
from pathlib import Path
from datetime import datetime
import hashlib

try:
    import requests
except ImportError:
    requests = None


class WhiteHatWorker:
    """White hat worker for auto-scanning dead addresses and suspicious wallets"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.kb_path = self.root / "knowledge_base"
        self.scraped_dir = self.kb_path / "scraped_data"
        self.wallet_dir = self.kb_path / "wallets"
        self.scan_results_file = self.kb_path / "whitehat_scans.json"

        # Load existing scan results
        self.scan_results = self.load_scan_results()

        # Wallet manager for storing found wallets
        try:
            from kana_wallet_manager import KanaWalletManager
            self.wallet_manager = KanaWalletManager()
        except ImportError:
            self.wallet_manager = None

    def load_scan_results(self):
        """Load previous scan results"""
        if self.scan_results_file.exists():
            with open(self.scan_results_file, 'r') as f:
                return json.load(f)
        return {"scans": [], "dead_addresses": [], "suspicious_wallets": []}

    def save_scan_results(self):
        """Save scan results"""
        with open(self.scan_results_file, 'w') as f:
            json.dump(self.scan_results, f, indent=2)

    def scan_scraped_content(self):
        """Scan all scraped content for wallet addresses"""
        if not self.scraped_dir.exists():
            print("[!] No scraped content found")
            return

        print("[*] Scanning scraped content for wallet addresses...\n")

        found_addresses = []
        suspicious_patterns = []

        # Ethereum/BSC/Polygon address regex
        eth_address_pattern = r'0x[a-fA-F0-9]{40}'
        # Contract addresses often start with specific patterns
        contract_patterns = [
            r'0x0000000000000000000000000000000000000000',  # Zero address
            r'0x[a-fA-F0-9]{40}',  # Any ETH address
        ]

        for scraped_file in self.scraped_dir.glob('scraped_*'):
            try:
                with open(scraped_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Find all Ethereum addresses
                addresses = re.findall(eth_address_pattern, content)

                for addr in addresses:
                    if addr not in found_addresses:
                        found_addresses.append(addr)

                        # Check for suspicious patterns
                        if self.is_suspicious_address(addr, content):
                            suspicious_patterns.append({
                                "address": addr,
                                "file": str(scraped_file.name),
                                "context": self.get_address_context(addr, content),
                                "reason": "suspicious_pattern"
                            })

            except Exception as e:
                print(f"[!] Error scanning {scraped_file.name}: {e}")

        # Analyze found addresses
        dead_addresses = []
        active_addresses = []

        print(f"[+] Found {len(found_addresses)} unique addresses")
        print(f"[+] {len(suspicious_patterns)} suspicious patterns detected\n")

        for addr in found_addresses:
            if self.is_dead_address(addr):
                dead_addresses.append(addr)
                print(f"[💀] Dead address: {addr}")
            else:
                active_addresses.append(addr)
                print(f"[✅] Active address: {addr}")

        # Save results
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "total_addresses": len(found_addresses),
            "dead_addresses": len(dead_addresses),
            "active_addresses": len(active_addresses),
            "suspicious_patterns": len(suspicious_patterns),
            "details": {
                "dead_list": dead_addresses,
                "suspicious": suspicious_patterns
            }
        }

        self.scan_results["scans"].append(scan_result)
        self.scan_results["dead_addresses"].extend(dead_addresses)
        self.scan_results["suspicious_wallets"].extend(suspicious_patterns)

        # Remove duplicates
        self.scan_results["dead_addresses"] = list(set(self.scan_results["dead_addresses"]))

        self.save_scan_results()

        # Auto-add dead addresses to wallet manager
        if self.wallet_manager:
            print(f"\n[*] Adding {len(dead_addresses)} dead addresses to wallet bank...")
            for addr in dead_addresses:
                wallet_name = f"DeadWallet_{addr[:8]}"
                self.wallet_manager.add_bank_account(wallet_name, addr, "eth", "whitehat_scan")

        print(f"\n[+] Scan complete! Results saved to {self.scan_results_file}")
        return scan_result

    def is_suspicious_address(self, address, content):
        """Check if address shows suspicious patterns"""
        suspicious_indicators = [
            "exploit", "vulnerability", "hack", "attack", "compromised",
            "phishing", "scam", "rugpull", "drain", "steal",
            "reentrancy", "delegatecall", "selfdestruct",
            "admin", "owner", "withdraw", "emergency",
            "backdoor", "malicious", "suspicious"
        ]

        context = self.get_address_context(address, content).lower()

        for indicator in suspicious_indicators:
            if indicator in context:
                return True

        return False

    def get_address_context(self, address, content, context_chars=200):
        """Get context around an address"""
        try:
            start = content.find(address)
            if start == -1:
                return ""

            start = max(0, start - context_chars // 2)
            end = min(len(content), start + context_chars)

            return content[start:end].replace('\n', ' ').strip()
        except:
            return ""

    def is_dead_address(self, address):
        """Check if address appears to be dead/inactive"""
        # Simple heuristics for dead addresses
        dead_patterns = [
            "0x0000000000000000000000000000000000000000",  # Zero address
            "0x" + "0" * 40,  # All zeros
            "0x" + "f" * 40,  # All F's
        ]

        if address in dead_patterns:
            return True

        # Check if address has many repeated characters (suspicious)
        if len(set(address[2:])) <= 5:  # Less than 5 unique characters
            return True

        return False

    def analyze_wallet_activity(self, address, chain="eth"):
        """Analyze wallet activity using blockchain explorers"""
        if not requests:
            return None, "[!] requests library not available"

        print(f"[*] Analyzing wallet activity: {address} on {chain}")

        try:
            if chain == "eth":
                url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey="
            elif chain == "bsc":
                url = f"https://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey="
            else:
                return None, f"[!] Chain {chain} not supported"

            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("status") == "1":
                txs = data.get("result", [])

                analysis = {
                    "address": address,
                    "chain": chain,
                    "total_txs": len(txs),
                    "first_tx": txs[0]["timeStamp"] if txs else None,
                    "last_tx": txs[-1]["timeStamp"] if txs else None,
                    "is_active": len(txs) > 0,
                    "risk_score": self.calculate_risk_score(txs)
                }

                return analysis, None
            else:
                return {"address": address, "is_active": False, "risk_score": 0}, None

        except Exception as e:
            return None, f"[!] Error analyzing wallet: {e}"

    def calculate_risk_score(self, transactions):
        """Calculate risk score based on transaction patterns"""
        if not transactions:
            return 0

        score = 0

        # Large transactions
        large_txs = [tx for tx in transactions if float(tx.get("value", 0)) > 1e18]  # > 1 ETH
        score += len(large_txs) * 10

        # Recent activity (last 30 days)
        recent_txs = []
        current_time = datetime.now().timestamp()

        for tx in transactions:
            if current_time - int(tx["timeStamp"]) < 30 * 24 * 60 * 60:  # 30 days
                recent_txs.append(tx)

        score += len(recent_txs) * 5

        # Unusual gas prices
        high_gas_txs = [tx for tx in transactions if int(tx.get("gasPrice", 0)) > 100 * 1e9]  # > 100 gwei
        score += len(high_gas_txs) * 2

        return min(score, 100)  # Cap at 100

    def auto_scan_and_report(self):
        """Automated scanning and reporting"""
        print("\n=== 🔍 WHITE HAT AUTO SCAN ===")
        print("[*] Scanning for dead addresses and suspicious wallets\n")

        # Scan scraped content
        scan_result = self.scan_scraped_content()

        if not scan_result:
            return

        # Analyze suspicious wallets
        print(f"\n[*] Analyzing {len(scan_result['details']['suspicious'])} suspicious wallets...")

        for wallet in scan_result["details"]["suspicious"]:
            analysis, error = self.analyze_wallet_activity(wallet["address"])

            if analysis:
                print(f"[📊] {wallet['address'][:10]}...: Risk Score {analysis['risk_score']}/100")
                wallet["analysis"] = analysis

        self.save_scan_results()

        # Generate report
        self.generate_scan_report(scan_result)

    def generate_scan_report(self, scan_result):
        """Generate a detailed scan report"""
        report_file = self.kb_path / f"whitehat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_file, 'w') as f:
            f.write("# White Hat Scan Report\n\n")
            f.write(f"**Scan Date:** {scan_result['timestamp']}\n\n")
            f.write(f"**Total Addresses Found:** {scan_result['total_addresses']}\n")
            f.write(f"**Dead Addresses:** {scan_result['dead_addresses']}\n")
            f.write(f"**Active Addresses:** {scan_result['active_addresses']}\n")
            f.write(f"**Suspicious Patterns:** {scan_result['suspicious_patterns']}\n\n")

            if scan_result["details"]["dead_list"]:
                f.write("## Dead Addresses Found\n\n")
                for addr in scan_result["details"]["dead_list"]:
                    f.write(f"- `{addr}`\n")
                f.write("\n")

            if scan_result["details"]["suspicious"]:
                f.write("## Suspicious Wallets\n\n")
                for wallet in scan_result["details"]["suspicious"]:
                    f.write(f"### {wallet['address']}\n")
                    f.write(f"**File:** {wallet['file']}\n")
                    f.write(f"**Reason:** {wallet['reason']}\n")
                    f.write(f"**Context:** {wallet['context'][:200]}...\n\n")

        print(f"[+] Report saved: {report_file}")

    def interactive_whitehat_worker(self):
        """Interactive white hat worker"""
        print("\n=== 🛡️ WHITE HAT WORKER ===")
        print("[*] Auto-scan for dead addresses and suspicious wallets\n")

        while True:
            print("[1] Scan scraped content for addresses")
            print("[2] Analyze specific wallet activity")
            print("[3] Auto scan and generate report")
            print("[4] View scan history")
            print("[5] List dead addresses")
            print("[0] Exit\n")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                self.scan_scraped_content()

            elif choice == '2':
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc): ").strip() or "eth"

                analysis, error = self.analyze_wallet_activity(address, chain)
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"\n[+] Wallet Analysis:")
                    print(f"   Address: {analysis['address']}")
                    print(f"   Chain: {analysis['chain']}")
                    print(f"   Total TXs: {analysis['total_txs']}")
                    print(f"   Active: {analysis['is_active']}")
                    print(f"   Risk Score: {analysis['risk_score']}/100")

            elif choice == '3':
                self.auto_scan_and_report()

            elif choice == '4':
                if self.scan_results["scans"]:
                    print(f"\n[+] Scan History ({len(self.scan_results['scans'])} scans):")
                    for i, scan in enumerate(self.scan_results["scans"][-5:], 1):  # Last 5
                        print(f"   {i}. {scan['timestamp'][:19]} - {scan['total_addresses']} addresses")
                else:
                    print("[!] No scan history found")

            elif choice == '5':
                if self.scan_results["dead_addresses"]:
                    print(f"\n[+] Dead Addresses ({len(self.scan_results['dead_addresses'])}):")
                    for addr in self.scan_results["dead_addresses"]:
                        print(f"   {addr}")
                else:
                    print("[!] No dead addresses found")

            elif choice == '0':
                break


if __name__ == "__main__":
    worker = WhiteHatWorker()
    worker.interactive_whitehat_worker()
