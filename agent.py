import os, time, requests, subprocess, threading, queue, json, re, hashlib
from datetime import datetime
from collections import defaultdict
import websocket
import logging
from typing import Dict, List, Optional, Tuple
import web3
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct

class KanaOmniReaper:
    def __init__(self):
        self.api_key = "AN4M57CM4CIDF24EE3AP2G9H2BBEFQVC6E"
        self.log_file = "logs/money_found.log"
        self.risk_log = "logs/risk_assessment.log"
        self.base_url = "https://api.bscscan.com/api"
        self.wss_url = "wss://bsc-ws-node.nariox.org:443"  # WebSocket endpoint
        self.target_queue = queue.Queue()
        self.risk_queue = queue.Queue()
        self.workers = 12  # Increased workers
        self.audit_workers = 6  # Separate audit workers
        self.risk_threshold = 7.5  # Risk score threshold

        # Enhanced patterns for vulnerability detection
        self.vuln_patterns = {
            'ownerless': re.compile(r'(?i)(?!.*onlyowner).*withdraw|transfer.*value', re.DOTALL),
            'reentrancy': re.compile(r'\.call\{value:\s*\w+\}'),
            'overflow': re.compile(r'\w+\s*\+\=\s*\w+.*[^>]=[^=]'),
            'delegatecall': re.compile(r'delegatecall'),
            'selfdestruct': re.compile(r'selfdestruct|suicide'),
            'payable_fallback': re.compile(r'function\s*\(\)\s*payable'),
            'unprotected_function': re.compile(r'function\s+\w+\s*\([^)]*\)\s*(?!.*onlyowner)(?!.*modifier)'),
        }

        # Risk scoring weights
        self.risk_weights = {
            'ownerless': 3.0,
            'reentrancy': 4.0,
            'overflow': 2.5,
            'delegatecall': 3.5,
            'selfdestruct': 4.5,
            'payable_fallback': 2.0,
            'unprotected_function': 1.5,
        }

        os.makedirs("logs", exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        """Setup enhanced logging"""
        logging.basicConfig(
            filename='logs/reaper_activity.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('KanaReaper')

    def websocket_monitor(self):
        """Real-time WebSocket monitoring for instant contract detection"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if 'params' in data and 'result' in data['params']:
                    txs = data['params']['result']
                    if isinstance(txs, list):
                        for tx in txs:
                            if tx.get('to') == '' and tx.get('contractAddress'):
                                contract_addr = tx['contractAddress']
                                self.target_queue.put(contract_addr)
                                self.logger.info(f"WS: New contract detected - {contract_addr}")
            except Exception as e:
                self.logger.error(f"WebSocket message error: {e}")

        def on_error(ws, error):
            self.logger.error(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            self.logger.warning("WebSocket connection closed, reconnecting...")
            time.sleep(5)
            self.websocket_monitor()

        def on_open(ws):
            # Subscribe to new blocks
            subscription = {
                "jsonrpc": "2.0",
                "method": "eth_subscribe",
                "params": ["newHeads"],
                "id": 1
            }
            ws.send(json.dumps(subscription))
            self.logger.info("WebSocket connected and subscribed to new blocks")

        while True:
            try:
                ws = websocket.WebSocketApp(
                    self.wss_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open
                )
                ws.run_forever()
            except Exception as e:
                self.logger.error(f"WebSocket connection failed: {e}")
                time.sleep(10)

    def get_new_contracts(self):
        """Enhanced polling backup for WebSocket failures"""
        last_block = None
        while True:
            try:
                # Get latest block number
                params = {
                    "module": "block",
                    "action": "getblocknobytime",
                    "timestamp": int(time.time()),
                    "closest": "before",
                    "apikey": self.api_key
                }
                r = requests.get(self.base_url, params=params, timeout=10).json()

                if r["status"] == "1":
                    block_number = r["result"]

                    # Only process if it's a new block
                    if last_block != block_number:
                        last_block = block_number
                        self.logger.info(f"Processing block: {block_number}")

                        # Get block transactions
                        params = {
                            "module": "block",
                            "action": "getblock",
                            "blockno": block_number,
                            "apikey": self.api_key
                        }
                        r = requests.get(self.base_url, params=params, timeout=10).json()

                        if r["status"] == "1":
                            contracts_found = 0
                            for tx in r["result"]["transactions"]:
                                if not tx["to"] and tx.get("contractAddress"):
                                    contract_addr = tx["contractAddress"]
                                    self.target_queue.put(contract_addr)
                                    contracts_found += 1

                            if contracts_found > 0:
                                self.logger.info(f"Found {contracts_found} new contracts in block {block_number}")

            except Exception as e:
                self.logger.error(f"Block monitoring error: {e}")

            time.sleep(3)  # Faster polling as backup

    def calculate_risk_score(self, source_code):
        """Calculate comprehensive risk score for contract"""
        score = 0.0
        findings = []

        for vuln_type, pattern in self.vuln_patterns.items():
            matches = pattern.findall(source_code)
            if matches:
                score += self.risk_weights[vuln_type] * len(matches)
                findings.append(f"{vuln_type}: {len(matches)} instances")

        # Additional checks
        if len(source_code) < 1000:
            score += 1.0  # Small contracts might be honeypots
            findings.append("small_contract: potential honeypot")

        if "pragma solidity" in source_code:
            # Check Solidity version
            version_match = re.search(r'pragma solidity\s+([^;]+)', source_code)
            if version_match:
                version = version_match.group(1)
                if "<0.8" in version:
                    score += 2.0  # Older versions have more vulnerabilities
                    findings.append(f"old_solidity_version: {version}")

        return round(score, 2), findings

    def audit_engine(self):
        """Enhanced audit engine with risk scoring"""
        while True:
            addr = self.target_queue.get()
            time.sleep(0.5)  # Rate limiting

            try:
                params = {
                    "module": "contract",
                    "action": "getsourcecode",
                    "address": addr,
                    "apikey": self.api_key
                }
                r = requests.get(self.base_url, params=params, timeout=15).json()

                if r["status"] == "1" and r["result"]:
                    contract_data = r["result"][0]
                    source_code = contract_data.get("SourceCode", "")

                    if source_code:
                        # Calculate risk score
                        risk_score, findings = self.calculate_risk_score(source_code)

                        # Log all contracts with their risk scores
                        with open(self.risk_log, "a", encoding='utf-8') as f:
                            f.write(f"[{datetime.now()}] {addr} | Risk: {risk_score} | Findings: {', '.join(findings)}\n")

                        # High-risk contracts get special attention
                        if risk_score >= self.risk_threshold:
                            print(f"🚨 [HIGH RISK] {addr} - Score: {risk_score}")
                            print(f"   Findings: {', '.join(findings)}")

                            # Log to money_found.log for high-risk contracts
                            with open(self.log_file, "a") as f:
                                f.write(f"[{datetime.now()}] HIGH_RISK: {addr} | Score: {risk_score}\n")

                        elif risk_score >= 5.0:
                            print(f"⚠️ [MEDIUM RISK] {addr} - Score: {risk_score}")

                        # All contracts get logged for analysis
                        self.logger.info(f"Audited {addr} - Risk Score: {risk_score}")

            except Exception as e:
                self.logger.error(f"Audit error for {addr}: {e}")

            self.target_queue.task_done()

    def performance_monitor(self):
        """Monitor scanning performance"""
        while True:
            queue_size = self.target_queue.qsize()
            if queue_size > 50:
                print(f"⚡ [PERFORMANCE] Queue backlog: {queue_size} contracts")
            time.sleep(30)

    def cloud_sync(self):
        """Enhanced cloud sync with error handling"""
        while True:
            time.sleep(300)  # Sync every 5 minutes
            try:
                result = subprocess.run(
                    "git add . && git commit -m 'Live_Scan_Update' && git push origin main --force",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print("[*] Cloud Synced Successfully")
                    self.logger.info("Cloud sync completed")
                else:
                    self.logger.error(f"Cloud sync failed: {result.stderr}")
            except Exception as e:
                self.logger.error(f"Cloud sync error: {e}")

    def run(self):
        print(f"=== 💀 KANA REAPER LIVE SCAN ACTIVE 💀 ===")
        print(f"Workers: {self.workers} scanners + {self.audit_workers} auditors")
        print(f"Risk Threshold: {self.risk_threshold}")
        print(f"WebSocket: {self.wss_url}")
        print("=" * 50)

        # Start WebSocket real-time monitoring
        threading.Thread(target=self.websocket_monitor, daemon=True).start()

        # Start polling backup
        threading.Thread(target=self.get_new_contracts, daemon=True).start()

        # Start cloud sync
        threading.Thread(target=self.cloud_sync, daemon=True).start()

        # Start performance monitor
        threading.Thread(target=self.performance_monitor, daemon=True).start()

        # Start audit workers
        for i in range(self.audit_workers):
            t = threading.Thread(target=self.audit_engine, daemon=True)
            t.start()
            print(f"[+] Audit Worker {i+1} started")

        print("\n[*] Live scanning active... Monitoring BSC in real-time")
        print("[*] Check logs/ for detailed analysis")
        print("[*] High-risk contracts will be highlighted\n")

        while True:
            time.sleep(1)


if __name__ == "__main__":
    try:
        reaper = KanaOmniReaper()
        reaper.run()
    except KeyboardInterrupt:
        print("\n[!] Reaper stopped by user")
    except Exception as e:
        print(f"[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()