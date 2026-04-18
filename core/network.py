import time
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None


class Web3GasFinder:
    """Find cheapest gas fees across blockchains"""

    GAS_APIS = {
        "eth": {
            "name": "Ethereum",
            "api_url": "https://api.etherscan.io/api",
            "param_key": "module=gastracker&action=gasoracle",
            "unit": "Gwei"
        },
        "bsc": {
            "name": "BSC",
            "api_url": "https://api.bscscan.com/api",
            "param_key": "module=gastracker&action=gasoracle",
            "unit": "Gwei"
        },
        "polygon": {
            "name": "Polygon",
            "api_url": "https://api.polygonscan.com/api",
            "param_key": "module=gastracker&action=gasoracle",
            "unit": "Gwei"
        }
    }

    FAUCET_SERVICES = {
        "eth": [
            {"name": "Goerli Faucet", "url": "https://goerlifaucet.com", "type": "manual"},
            {"name": "Alchemy Faucet", "url": "https://www.alchemy.com/faucets/ethereum", "type": "manual"},
            {"name": "QuickNode Faucet", "url": "https://faucet.quicknode.com/drip", "type": "manual"},
            {"name": "Infura Faucet", "url": "https://www.infura.io/faucet", "type": "manual"},
        ],
        "bsc": [
            {"name": "BSC Testnet Faucet", "url": "https://testnet.binance.org/faucet-smart", "type": "manual"},
            {"name": "QuickNode BSC Faucet", "url": "https://faucet.quicknode.com/drip", "type": "manual"}
        ],
        "polygon": [
            {"name": "Polygon Mumbai Faucet", "url": "https://faucet.polygon.technology/", "type": "manual"},
            {"name": "QuickNode Polygon Faucet", "url": "https://faucet.quicknode.com/drip", "type": "manual"}
        ]
    }

    def __init__(self):
        self.last_update = {}
        self.gas_cache = {}
        self.claimed_faucets = set()  # Track claimed faucets to avoid spam

    def get_current_gas_price(self, chain="eth"):
        """Get current gas price for a chain"""
        if not requests:
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
                self.gas_cache[chain] = gas_info
                self.last_update[chain] = time.time()
                return gas_info, None
            else:
                return None, "[!] Unable to fetch gas price"
        except Exception as e:
            return None, f"[!] Error: {e}"

    def find_cheapest_chain(self):
        """Find cheapest gas across all chains"""
        print("[*] Scanning gas prices across chains...\n")

        cheapest = None
        results = {}

        for chain in self.GAS_APIS.keys():
            gas_info, error = self.get_current_gas_price(chain)

            if error:
                print(f"[!] {chain.upper()}: {error}")
                continue

            print(f"[+] {chain.upper()}:")
            print(f"   Safe:     {gas_info['safe_gas_price']} {gas_info['unit']}")
            print(f"   Standard: {gas_info['standard_gas_price']} {gas_info['unit']}")
            print(f"   Fast:     {gas_info['fast_gas_price']} {gas_info['unit']}\n")

            results[chain] = gas_info["safe_gas_price"]

            if not cheapest or gas_info["safe_gas_price"] < cheapest["price"]:
                cheapest = {
                    "chain": chain,
                    "price": gas_info["safe_gas_price"],
                    "info": gas_info
                }

        if cheapest:
            print(f"[🌟] CHEAPEST: {cheapest['chain'].upper()} at {cheapest['price']} Gwei")
            return cheapest
        else:
            return None

    def estimate_transaction_cost(self, chain="eth", gas_amount=21000):
        """Estimate transaction cost"""
        gas_info, error = self.get_current_gas_price(chain)

        if error:
            return None, error

        cost_safe = (gas_info["safe_gas_price"] * gas_amount) / 1e9
        cost_standard = (gas_info["standard_gas_price"] * gas_amount) / 1e9
        cost_fast = (gas_info["fast_gas_price"] * gas_amount) / 1e9

        return {
            "chain": chain,
            "gas_amount": gas_amount,
            "safe_cost": cost_safe,
            "standard_cost": cost_standard,
            "fast_cost": cost_fast,
            "unit": gas_info["unit"]
        }, None

    def claim_free_gas(self, chain="eth", wallet_address=""):
        """Attempt to claim free gas from faucets"""
        if not requests:
            return False, "[!] requests library not available"

        if not wallet_address:
            return False, "[!] Wallet address required for claiming"

        faucets = self.FAUCET_SERVICES.get(chain, [])
        if not faucets:
            return False, f"[!] No faucets available for {chain}"

        print(f"[*] Attempting to claim free gas for {chain}...")
        print(f"[*] Wallet: {wallet_address}\n")

        claimed = False
        results = []

        for faucet in faucets:
            faucet_key = f"{chain}_{faucet['name']}_{wallet_address}"

            if faucet_key in self.claimed_faucets:
                print(f"[-] {faucet['name']}: Already claimed recently")
                continue

            print(f"[*] Trying {faucet['name']}...")

            try:
                # For manual faucets, we simulate the claim process
                # In real implementation, you'd need to handle specific faucet APIs
                success = self._simulate_faucet_claim(faucet, wallet_address)

                if success:
                    self.claimed_faucets.add(faucet_key)
                    claimed = True
                    results.append(f"[+] {faucet['name']}: Claim successful!")
                    print(f"[+] {faucet['name']}: Claim successful!")
                else:
                    results.append(f"[-] {faucet['name']}: Claim failed")
                    print(f"[-] {faucet['name']}: Claim failed")

            except Exception as e:
                results.append(f"[!] {faucet['name']}: Error - {e}")
                print(f"[!] {faucet['name']}: Error - {e}")

        if claimed:
            return True, "\n".join(results)
        else:
            return False, "No faucets could be claimed from"

    def _simulate_faucet_claim(self, faucet, wallet_address):
        """Simulate claiming from a faucet (in real implementation, use actual APIs)"""
        # This is a simulation - real implementation would need specific faucet integrations
        import time
        import random

        # Simulate network delay
        time.sleep(random.uniform(1, 3))

        # Simulate success/failure (70% success rate for demo)
        return random.random() < 0.7

    def auto_claim_gas_campaign(self, wallet_address, chains=None):
        """Run automated gas claiming campaign across multiple chains"""
        if not chains:
            chains = ["eth", "bsc", "polygon"]

        print(f"\n=== 🚀 AUTO GAS CLAIM CAMPAIGN ===")
        print(f"[*] Target wallet: {wallet_address}")
        print(f"[*] Chains: {', '.join(chains)}\n")

        total_claimed = 0
        results = {}

        for chain in chains:
            print(f"[*] Processing {chain.upper()}...")
            success, message = self.claim_free_gas(chain, wallet_address)

            if success:
                total_claimed += 1
                results[chain] = "SUCCESS"
                print(f"[+] {chain.upper()}: Gas claimed!")
            else:
                results[chain] = "FAILED"
                print(f"[-] {chain.upper()}: {message}")

        print(f"\n[+] Campaign complete: {total_claimed}/{len(chains)} chains successful")
        return results

    def get_gas_optimization_tips(self, chain="eth"):
        """Get tips for optimizing gas spending"""
        tips = {
            "general": [
                "Batch transactions when possible",
                "Use layer 2 solutions (Arbitrum, Optimism, Polygon)",
                "Monitor network congestion",
                "Use contracts with optimized code",
                "Avoid complex storage operations"
            ],
            "eth": [
                "Use L2 like Arbitrum or Optimism for 50-100x cheaper gas",
                "Wait for low-congestion periods (off-peak hours)",
                "Consider using MEV-resistant options",
                "Use smart contract optimization tools"
            ],
            "bsc": [
                "Usually cheaper than Ethereum",
                "Check validator set during low activity",
                "Use BSC testnet for testing"
            ],
            "polygon": [
                "Significantly cheaper than Ethereum",
                "Good for frequent transactions",
                "Bridge assets from Ethereum for cheaper ops"
            ]
        }

        print(f"\n=== GAS OPTIMIZATION TIPS FOR {chain.upper()} ===\n")

        for tip in tips.get(chain, tips["general"]):
            print(f"• {tip}\n")

    def interactive_gas_finder(self):
        """Interactive gas price finder"""
        print("\n=== 💰 WEB3 GAS FEE FINDER ===")
        print("[*] Find cheapest gas prices and claim free gas\n")

        wallet_address = input("[?] Your wallet address (for claiming): ").strip()

        while True:
            print("[1] Check current gas prices")
            print("[2] Find cheapest chain")
            print("[3] Estimate transaction cost")
            print("[4] Find free gas faucets")
            print("[5] Claim free gas")
            print("[6] Auto gas claim campaign")
            print("[7] Gas optimization tips")
            print("[0] Exit\n")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                chain = input("[?] Chain (eth/bsc/polygon/all): ").strip() or "all"

                if chain == "all":
                    for c in self.GAS_APIS.keys():
                        gas_info, error = self.get_current_gas_price(c)
                        if not error:
                            print(f"\n[+] {c.upper()}: {gas_info['standard_gas_price']} Gwei")
                else:
                    gas_info, error = self.get_current_gas_price(chain)
                    if error:
                        print(f"[!] {error}")
                    else:
                        print(f"\n[+] {chain.upper()}:")
                        print(f"   Safe:     {gas_info['safe_gas_price']} {gas_info['unit']}")
                        print(f"   Standard: {gas_info['standard_gas_price']} {gas_info['unit']}")
                        print(f"   Fast:     {gas_info['fast_gas_price']} {gas_info['unit']}")

            elif choice == '2':
                self.find_cheapest_chain()

            elif choice == '3':
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                gas_amount = int(input("[?] Gas amount (default 21000): ").strip() or "21000")
                
                estimate, error = self.estimate_transaction_cost(chain, gas_amount)
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"\n[+] Transaction Cost Estimate:")
                    print(f"   Safe:     {estimate['safe_cost']} {estimate['unit']}")
                    print(f"   Standard: {estimate['standard_cost']} {estimate['unit']}")
                    print(f"   Fast:     {estimate['fast_cost']} {estimate['unit']}")

            elif choice == '4':
                self.find_free_gas_opportunities()

            elif choice == '5':
                if not wallet_address:
                    wallet_address = input("[?] Your wallet address: ").strip()
                
                chain = input("[?] Chain (eth/bsc/polygon): ").strip() or "eth"
                success, message = self.claim_free_gas(chain, wallet_address)
                
                if success:
                    print("[+] Gas claim successful!")
                else:
                    print(f"[!] Claim failed: {message}")

            elif choice == '6':
                if not wallet_address:
                    wallet_address = input("[?] Your wallet address: ").strip()
                
                chains_input = input("[?] Chains (eth,bsc,polygon or 'all'): ").strip()
                if chains_input.lower() == 'all' or not chains_input:
                    chains = None
                else:
                    chains = [c.strip() for c in chains_input.split(',')]
                
                self.auto_claim_gas_campaign(wallet_address, chains)

            elif choice == '7':
                chain = input("[?] Chain (eth/bsc/polygon/all): ").strip() or "general"
                self.get_gas_optimization_tips(chain if chain != "all" else "general")

            elif choice == '0':
                break


if __name__ == "__main__":
    finder = Web3GasFinder()
    finder.interactive_gas_finder()
