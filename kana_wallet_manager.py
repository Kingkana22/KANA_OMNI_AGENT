import os
import json
from pathlib import Path
from datetime import datetime
import hashlib

try:
    import requests
except ImportError:
    requests = None


class KanaWalletManager:
    """Personal wallet manager for KANA ecosystem"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.wallet_dir = self.root / "knowledge_base" / "wallets"
        self.wallet_dir.mkdir(exist_ok=True)
        self.bank_file = self.wallet_dir / "bank_accounts.json"
        self.personal_wallet_file = self.wallet_dir / "personal_wallet.json"
        self.load_wallets()

    def load_wallets(self):
        """Load wallet data"""
        # Personal wallet
        if self.personal_wallet_file.exists():
            with open(self.personal_wallet_file, 'r') as f:
                self.personal_wallet = json.load(f)
        else:
            self.personal_wallet = {
                "address": "",
                "balance": 0,
                "chain": "eth",
                "created": datetime.now().isoformat(),
                "transactions": []
            }

        # Bank accounts (death wallets)
        if self.bank_file.exists():
            with open(self.bank_file, 'r') as f:
                self.bank_accounts = json.load(f)
        else:
            self.bank_accounts = {}

    def save_wallets(self):
        """Save wallet data"""
        with open(self.personal_wallet_file, 'w') as f:
            json.dump(self.personal_wallet, f, indent=2)

        with open(self.bank_file, 'w') as f:
            json.dump(self.bank_accounts, f, indent=2)

    def set_personal_wallet(self, address, chain="eth"):
        """Set personal wallet address"""
        self.personal_wallet["address"] = address
        self.personal_wallet["chain"] = chain
        self.save_wallets()
        print(f"[+] Personal wallet set: {address} ({chain})")

    def add_bank_account(self, name, address, chain="eth", source="scraping"):
        """Add death wallet to bank"""
        wallet_id = hashlib.md5(f"{name}{address}{chain}".encode()).hexdigest()[:8]

        self.bank_accounts[wallet_id] = {
            "name": name,
            "address": address,
            "chain": chain,
            "source": source,
            "added": datetime.now().isoformat(),
            "balance": 0,
            "status": "active",
            "coding_efforts": 0,  # Points earned from coding tasks
            "transactions": []
        }

        self.save_wallets()
        print(f"[+] Bank account added: {name} ({wallet_id})")
        return wallet_id

    def earn_coding_points(self, wallet_id, points, reason="coding_task"):
        """Earn points from coding efforts"""
        if wallet_id in self.bank_accounts:
            self.bank_accounts[wallet_id]["coding_efforts"] += points
            self.bank_accounts[wallet_id]["transactions"].append({
                "type": "earn",
                "points": points,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            self.save_wallets()
            print(f"[+] Earned {points} points for {wallet_id} ({reason})")

    def withdraw_to_personal(self, wallet_id, amount=None):
        """Withdraw from bank account to personal wallet"""
        if wallet_id not in self.bank_accounts:
            print("[!] Bank account not found")
            return False

        account = self.bank_accounts[wallet_id]

        if amount is None:
            amount = account["coding_efforts"]

        if amount > account["coding_efforts"]:
            print(f"[!] Insufficient points. Available: {account['coding_efforts']}")
            return False

        # Deduct from bank
        account["coding_efforts"] -= amount
        account["transactions"].append({
            "type": "withdraw",
            "amount": amount,
            "to": self.personal_wallet["address"],
            "timestamp": datetime.now().isoformat()
        })

        # Add to personal
        self.personal_wallet["balance"] += amount
        self.personal_wallet["transactions"].append({
            "type": "deposit",
            "amount": amount,
            "from": wallet_id,
            "timestamp": datetime.now().isoformat()
        })

        self.save_wallets()
        print(f"[+] Withdrew {amount} points from {wallet_id} to personal wallet")
        return True

    def get_bank_balance(self):
        """Get total bank balance"""
        total = sum(account["coding_efforts"] for account in self.bank_accounts.values())
        return total

    def list_bank_accounts(self):
        """List all bank accounts"""
        if not self.bank_accounts:
            print("[!] No bank accounts found")
            return

        print(f"\n=== 💰 KANA BANK ACCOUNTS ({len(self.bank_accounts)}) ===\n")

        for wallet_id, account in self.bank_accounts.items():
            print(f"[{wallet_id}] {account['name']}")
            print(f"   Address: {account['address']} ({account['chain']})")
            print(f"   Balance: {account['coding_efforts']} points")
            print(f"   Source: {account['source']}")
            print(f"   Status: {account['status']}\n")

    def interactive_wallet_manager(self):
        """Interactive wallet management"""
        print("\n=== 💳 KANA WALLET MANAGER ===")
        print("[*] Manage personal wallet and bank accounts\n")

        while True:
            print("[1] Set personal wallet")
            print("[2] View personal wallet")
            print("[3] Add bank account (death wallet)")
            print("[4] List bank accounts")
            print("[5] Earn coding points")
            print("[6] Withdraw to personal wallet")
            print("[7] Bank balance summary")
            print("[0] Exit\n")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                self.set_personal_wallet(address, chain)

            elif choice == '2':
                print(f"\n[+] Personal Wallet:")
                print(f"   Address: {self.personal_wallet['address']}")
                print(f"   Chain: {self.personal_wallet['chain']}")
                print(f"   Balance: {self.personal_wallet['balance']} points")
                print(f"   Created: {self.personal_wallet['created']}")

            elif choice == '3':
                name = input("[?] Account name: ").strip()
                address = input("[?] Wallet address: ").strip()
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                source = input("[?] Source (scraping/manual): ").strip() or "manual"
                self.add_bank_account(name, address, chain, source)

            elif choice == '4':
                self.list_bank_accounts()

            elif choice == '5':
                self.list_bank_accounts()
                wallet_id = input("[?] Select wallet ID: ").strip()
                points = int(input("[?] Points to earn: ").strip() or "10")
                reason = input("[?] Reason: ").strip() or "coding_task"
                self.earn_coding_points(wallet_id, points, reason)

            elif choice == '6':
                self.list_bank_accounts()
                wallet_id = input("[?] Select wallet ID: ").strip()
                amount = input("[?] Amount (leave empty for all): ").strip()
                amount = int(amount) if amount else None
                self.withdraw_to_personal(wallet_id, amount)

            elif choice == '7':
                total_bank = self.get_bank_balance()
                personal = self.personal_wallet["balance"]
                print(f"\n[+] Bank Total: {total_bank} points")
                print(f"[+] Personal: {personal} points")
                print(f"[+] Grand Total: {total_bank + personal} points")

            elif choice == '0':
                break


if __name__ == "__main__":
    manager = KanaWalletManager()
    manager.interactive_wallet_manager()
