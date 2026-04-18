import re
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    requests = None


class DeathWalletTracker:
    """Track founder/creator wallets across chains"""
    
    CHAIN_EXPLORERS = {
        "eth": {
            "name": "Ethereum",
            "explorer": "https://api.etherscan.io/api",
            "symbol": "ETH"
        },
        "bsc": {
            "name": "Binance Smart Chain",
            "explorer": "https://api.bscscan.com/api",
            "symbol": "BNB"
        },
        "polygon": {
            "name": "Polygon",
            "explorer": "https://api.polygonscan.com/api",
            "symbol": "MATIC"
        },
        "arbitrum": {
            "name": "Arbitrum",
            "explorer": "https://api.arbiscan.io/api",
            "symbol": "ARB"
        },
        "optimism": {
            "name": "Optimism",
            "explorer": "https://api-optimistic.etherscan.io/api",
            "symbol": "OP"
        }
    }

    def __init__(self):
        self.repo_root = Path(__file__).resolve().parent
        self.kb_path = self.repo_root / "knowledge_base"
        self.tracker_dir = self.kb_path / "wallet_tracking"
        self.tracker_dir.mkdir(parents=True, exist_ok=True)
        self.api_keys = self.load_api_keys()
        self.tracked_wallets = self.load_tracked_wallets()

    def load_api_keys(self):
        """Load API keys dari environment atau config"""
        import os
        return {
            "etherscan": os.getenv("ETHERSCAN_API_KEY", ""),
            "bscscan": os.getenv("BSCSCAN_API_KEY", ""),
            "polygonscan": os.getenv("POLYGONSCAN_API_KEY", ""),
        }

    def load_tracked_wallets(self):
        """Load wallet tracking data"""
        wallet_file = self.tracker_dir / "tracked_wallets.json"
        if wallet_file.exists():
            with open(wallet_file, 'r') as f:
                return json.load(f)
        return {}

    def save_tracked_wallets(self):
        """Save wallet tracking data"""
        wallet_file = self.tracker_dir / "tracked_wallets.json"
        with open(wallet_file, 'w') as f:
            json.dump(self.tracked_wallets, f, indent=2)

    def add_wallet(self, address, label="", chain="eth"):
        """Add wallet to tracking list"""
        if address not in self.tracked_wallets:
            self.tracked_wallets[address] = {
                "label": label,
                "chain": chain,
                "added_at": datetime.now().isoformat(),
                "transactions": [],
                "alerts": []
            }
            self.save_tracked_wallets()
            return True, f"Wallet {address} added to tracking"
        return False, f"Wallet {address} already tracked"

    def get_wallet_balance(self, address, chain="eth"):
        """Get wallet balance from blockchain explorer"""
        if not requests:
            return None, "[!] requests library not available"

        chain_info = self.CHAIN_EXPLORERS.get(chain)
        if not chain_info:
            return None, f"[!] Chain {chain} not supported"

        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "apikey": self.api_keys.get(f"{chain}scan", "")
        }

        try:
            response = requests.get(chain_info["explorer"], params=params, timeout=10)
            data = response.json()

            if data.get("status") == "1":
                balance = int(data.get("result", 0)) / 1e18
                return balance, None
            else:
                return None, f"[!] {data.get('message', 'API error')}"
        except Exception as e:
            return None, f"[!] Error fetching balance: {e}"

    def get_wallet_transactions(self, address, chain="eth", limit=10):
        """Get recent wallet transactions"""
        if not requests:
            return None, "[!] requests library not available"

        chain_info = self.CHAIN_EXPLORERS.get(chain)
        if not chain_info:
            return None, f"[!] Chain {chain} not supported"

        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": limit,
            "sort": "desc",
            "apikey": self.api_keys.get(f"{chain}scan", "")
        }

        try:
            response = requests.get(chain_info["explorer"], params=params, timeout=10)
            data = response.json()

            if data.get("status") == "1":
                txs = data.get("result", [])
                return txs, None
            else:
                return None, f"[!] {data.get('message', 'No transactions')}"
        except Exception as e:
            return None, f"[!] Error fetching transactions: {e}"

    def analyze_wallet_activity(self, address, chain="eth", days=30):
        """Analyze wallet activity patterns"""
        txs, error = self.get_wallet_transactions(address, chain, limit=100)

        if error:
            return None, error

        if not txs:
            return None, "[!] No transactions found"

        analysis = {
            "address": address,
            "chain": chain,
            "total_txs": len(txs),
            "recent_activity": [],
            "total_outgoing": 0,
            "total_incoming": 0,
            "patterns": {}
        }

        cutoff_time = datetime.now() - timedelta(days=days)

        for tx in txs[:50]:
            try:
                tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
                if tx_time < cutoff_time:
                    break

                value = int(tx.get("value", 0)) / 1e18
                tx_from = tx.get("from", "").lower()
                tx_to = tx.get("to", "").lower()

                if tx_from == address.lower():
                    analysis["total_outgoing"] += value
                    direction = "OUT"
                else:
                    analysis["total_incoming"] += value
                    direction = "IN"

                analysis["recent_activity"].append({
                    "hash": tx.get("hash"),
                    "timestamp": tx.get("timeStamp"),
                    "direction": direction,
                    "value": value,
                    "to": tx_to,
                    "from": tx_from
                })
            except:
                continue

        return analysis, None

    def detect_suspicious_activity(self, address, chain="eth"):
        """Detect suspicious wallet activity"""
        analysis, error = self.analyze_wallet_activity(address, chain, days=7)

        if error:
            return None, error

        suspicious = {
            "address": address,
            "alerts": [],
            "risk_score": 0
        }

        # Check for rapid outflows
        if analysis["total_outgoing"] > analysis["total_incoming"] * 5:
            suspicious["alerts"].append("High outflow compared to inflow")
            suspicious["risk_score"] += 20

        # Check for pattern changes
        if len(analysis["recent_activity"]) > 20:
            avg_tx = sum(tx["value"] for tx in analysis["recent_activity"]) / len(analysis["recent_activity"])
            large_txs = [tx for tx in analysis["recent_activity"] if tx["value"] > avg_tx * 10]

            if large_txs:
                suspicious["alerts"].append(f"{len(large_txs)} unusually large transactions detected")
                suspicious["risk_score"] += 15

        # Check for unusual receiver patterns
        receivers = {}
        for tx in analysis["recent_activity"]:
            if tx["direction"] == "OUT":
                receiver = tx["to"]
                receivers[receiver] = receivers.get(receiver, 0) + 1

        if receivers:
            most_frequent = max(receivers.items(), key=lambda x: x[1])
            if most_frequent[1] > 3:
                suspicious["alerts"].append(f"Frequent transactions to {most_frequent[0]}")
                suspicious["risk_score"] += 10

        return suspicious, None

    def track_founder_wallet(self, contract_address, chain="eth"):
        """Extract and track founder wallet from contract"""
        if not requests:
            return None, "[!] requests library not available"

        chain_info = self.CHAIN_EXPLORERS.get(chain)
        if not chain_info:
            return None, f"[!] Chain {chain} not supported"

        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": contract_address,
            "apikey": self.api_keys.get(f"{chain}scan", "")
        }

        try:
            response = requests.get(chain_info["explorer"], params=params, timeout=10)
            data = response.json()

            if data.get("status") == "1":
                contract_info = data.get("result", [{}])[0]
                creator = contract_info.get("Creator", "").split(",")[0].strip()

                result = {
                    "contract": contract_address,
                    "creator": creator,
                    "contract_name": contract_info.get("ContractName"),
                    "chain": chain,
                    "source_code": contract_info.get("SourceCode", "")[:500]
                }

                if creator:
                    self.add_wallet(creator, f"Creator of {contract_info.get('ContractName', 'Unknown')}", chain)

                return result, None
            else:
                return None, "[!] Contract not found"
        except Exception as e:
            return None, f"[!] Error: {e}"

    def interactive_tracking(self):
        """Interactive wallet tracking menu"""
        print("\n=== 💀 DEATH WALLET TRACKER ===")
        print("[*] Track founder wallets and monitor activity\n")

        while True:
            print("\n[1] Add wallet to tracking")
            print("[2] Check wallet balance")
            print("[3] Analyze wallet activity")
            print("[4] Detect suspicious activity")
            print("[5] Track contract creator")
            print("[6] View tracked wallets")
            print("[0] Exit\n")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                address = input("[?] Wallet address: ").strip()
                label = input("[?] Label (optional): ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                success, msg = self.add_wallet(address, label, chain)
                print(f"[+] {msg}")

            elif choice == '2':
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                balance, error = self.get_wallet_balance(address, chain)
                if error:
                    print(f"[!] {error}")
                else:
                    symbol = self.CHAIN_EXPLORERS[chain]["symbol"]
                    print(f"[+] Balance: {balance} {symbol}")

            elif choice == '3':
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                analysis, error = self.analyze_wallet_activity(address, chain)
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"\n[+] Activity Analysis:")
                    print(f"   Total TXs: {analysis['total_txs']}")
                    print(f"   Outgoing: {analysis['total_outgoing']}")
                    print(f"   Incoming: {analysis['total_incoming']}")

            elif choice == '4':
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                suspicious, error = self.detect_suspicious_activity(address, chain)
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"\n[+] Risk Score: {suspicious['risk_score']}/100")
                    for alert in suspicious['alerts']:
                        print(f"   ⚠️ {alert}")

            elif choice == '5':
                contract = input("[?] Contract address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                founder, error = self.track_founder_wallet(contract, chain)
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"[+] Creator: {founder['creator']}")
                    self.add_wallet(founder["creator"], f"Creator: {founder['contract_name']}", chain)

            elif choice == '6':
                if self.tracked_wallets:
                    print("\n[+] Tracked Wallets:")
                    for addr, info in list(self.tracked_wallets.items())[:5]:
                        print(f"   {addr} - {info['label']} ({info['chain']})")
                else:
                    print("[!] No tracked wallets")

            elif choice == '0':
                break


if __name__ == "__main__":
    tracker = DeathWalletTracker()
    tracker.interactive_tracking()
