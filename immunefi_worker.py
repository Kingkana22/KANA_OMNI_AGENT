import os
import re
import json
import time
from pathlib import Path
from datetime import datetime
import subprocess
import hashlib

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


class ImmunefiWorker:
    """Immunefi Bug Bounty Hunter - Automated bug hunting and POC creation"""

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.kb_path = self.root / "knowledge_base"
        self.immunefi_dir = self.kb_path / "immunefi_bounties"
        self.immunefi_dir.mkdir(exist_ok=True)

        self.bounties_file = self.immunefi_dir / "active_bounties.json"
        self.poc_dir = self.immunefi_dir / "pocs"
        self.poc_dir.mkdir(exist_ok=True)

        # Load existing bounties
        self.bounties = self.load_bounties()

        # GitHub token for API access
        self.github_token = os.getenv("GITHUB_TOKEN")

    def load_bounties(self):
        """Load active bounties data"""
        if self.bounties_file.exists():
            with open(self.bounties_file, 'r') as f:
                return json.load(f)
        return {"bounties": [], "submissions": []}

    def save_bounties(self):
        """Save bounties data"""
        with open(self.bounties_file, 'w') as f:
            json.dump(self.bounties, f, indent=2)

    def scrape_immunefi_bounties(self):
        """Scrape active bounties from Immunefi"""
        if not requests or not BeautifulSoup:
            return None, "[!] requests or beautifulsoup4 not available"

        print("[*] Scraping Immunefi for active bounties...\n")

        try:
            url = "https://immunefi.com/bug-bounty/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            bounties = []

            # Find bounty cards (this selector may need updating based on site changes)
            bounty_cards = soup.find_all('div', class_=re.compile(r'bounty.*card'))

            for card in bounty_cards[:10]:  # Limit to first 10
                try:
                    title_elem = card.find('h3') or card.find('h2') or card.find(class_=re.compile(r'title'))
                    title = title_elem.text.strip() if title_elem else "Unknown"

                    reward_elem = card.find(class_=re.compile(r'reward|prize|amount'))
                    reward = reward_elem.text.strip() if reward_elem else "Unknown"

                    link_elem = card.find('a', href=True)
                    link = link_elem['href'] if link_elem else ""

                    if not link.startswith('http'):
                        link = f"https://immunefi.com{link}"

                    bounty = {
                        "id": hashlib.md5(f"{title}{link}".encode()).hexdigest()[:8],
                        "title": title,
                        "reward": reward,
                        "url": link,
                        "scraped_at": datetime.now().isoformat(),
                        "status": "active"
                    }

                    bounties.append(bounty)
                    print(f"[+] Found: {title} - {reward}")

                except Exception as e:
                    continue

            # Save bounties
            for bounty in bounties:
                if not any(b['id'] == bounty['id'] for b in self.bounties["bounties"]):
                    self.bounties["bounties"].append(bounty)

            self.save_bounties()

            print(f"\n[+] Scraped {len(bounties)} bounties from Immunefi")
            return bounties, None

        except Exception as e:
            return None, f"[!] Error scraping Immunefi: {e}"

    def analyze_bounty_requirements(self, bounty_url):
        """Analyze specific bounty requirements"""
        if not requests or not BeautifulSoup:
            return None, "[!] requests or beautifulsoup4 not available"

        print(f"[*] Analyzing bounty: {bounty_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(bounty_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract requirements (this will need customization based on Immunefi structure)
            requirements = {
                "url": bounty_url,
                "title": "",
                "scope": [],
                "rewards": {},
                "rules": [],
                "technologies": []
            }

            # Try to extract title
            title_elem = soup.find('h1') or soup.find('title')
            requirements["title"] = title_elem.text.strip() if title_elem else "Unknown"

            # Extract scope (in-scope contracts/programs)
            scope_section = soup.find(class_=re.compile(r'scope|in-scope'))
            if scope_section:
                scope_items = scope_section.find_all(['li', 'p'])
                requirements["scope"] = [item.text.strip() for item in scope_items]

            # Extract technologies
            tech_indicators = ['solidity', 'web3', 'ethereum', 'smart contract', 'defi', 'nft']
            content_text = soup.get_text().lower()

            for tech in tech_indicators:
                if tech in content_text:
                    requirements["technologies"].append(tech.title())

            return requirements, None

        except Exception as e:
            return None, f"[!] Error analyzing bounty: {e}"

    def create_poc_template(self, bounty_id, requirements):
        """Create POC template for a bounty"""
        poc_file = self.poc_dir / f"poc_{bounty_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sol"

        template = f"""// Immunefi Bug Bounty POC
// Bounty: {requirements.get('title', 'Unknown')}
// URL: {requirements.get('url', 'Unknown')}
// Generated: {datetime.now().isoformat()}

pragma solidity ^0.8.0;

contract ImmunefiPOC {{
    // POC for vulnerability demonstration
    // TODO: Implement the actual exploit/vulnerability

    address public targetContract;
    address public attacker;

    constructor(address _target) {{
        targetContract = _target;
        attacker = msg.sender;
    }}

    // TODO: Add exploit function
    function exploit() public {{
        // Implement your exploit here
        // This is just a template - customize based on the vulnerability
        require(msg.sender == attacker, "Only attacker can execute");

        // Example: Reentrancy attack
        // targetContract.call(abi.encodeWithSignature("withdraw()"));

        // Example: Access control bypass
        // targetContract.call(abi.encodeWithSignature("changeOwner(address)", attacker));
    }}

    // Helper functions
    function getBalance() public view returns (uint256) {{
        return address(this).balance;
    }}

    function withdrawFunds() public {{
        require(msg.sender == attacker, "Only attacker can withdraw");
        payable(attacker).transfer(address(this).balance);
    }}

    // TODO: Add any additional functions needed for the POC
}}
"""

        with open(poc_file, 'w') as f:
            f.write(template)

        print(f"[+] POC template created: {poc_file}")
        return poc_file

    def create_test_script(self, bounty_id, poc_file):
        """Create test script for the POC"""
        test_file = poc_file.with_suffix('.js')

        test_template = f"""// Test script for Immunefi POC
// Bounty ID: {bounty_id}
// POC File: {poc_file.name}

const {{ ethers }} = require("hardhat");

describe("Immunefi POC Test", function () {{
    let pocContract;
    let targetContract;
    let attacker;
    let victim;

    beforeEach(async function () {{
        // Deploy target contract (replace with actual vulnerable contract)
        const TargetFactory = await ethers.getContractFactory("TargetContract");
        targetContract = await TargetFactory.deploy();
        await targetContract.deployed();

        // Deploy POC contract
        const POCFactory = await ethers.getContractFactory("ImmunefiPOC");
        pocContract = await POCFactory.deploy(targetContract.address);
        await pocContract.deployed();

        [attacker, victim] = await ethers.getSigners();
    }});

    it("Should demonstrate the vulnerability", async function () {{
        // TODO: Set up the scenario
        console.log("Target contract:", targetContract.address);
        console.log("POC contract:", pocContract.address);

        // TODO: Execute the exploit
        // await pocContract.exploit();

        // TODO: Verify the exploit worked
        // expect(await targetContract.someState()).to.equal(expectedValue);
    }});

    it("Should show the impact", async function () {{
        // TODO: Demonstrate the impact of the vulnerability
    }});
}});
"""

        with open(test_file, 'w') as f:
            f.write(test_template)

        print(f"[+] Test script created: {test_file}")
        return test_file

    def submit_bounty_report(self, bounty_id, poc_file, description):
        """Prepare bounty submission report"""
        submission = {
            "bounty_id": bounty_id,
            "poc_file": str(poc_file),
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        }

        self.bounties["submissions"].append(submission)
        self.save_bounties()

        # Create submission report
        report_file = self.immunefi_dir / f"submission_{bounty_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        report_content = f"""# Immunefi Bug Bounty Submission

## Bounty Information
- **ID:** {bounty_id}
- **Date:** {datetime.now().isoformat()}
- **Status:** Draft

## Vulnerability Description
{description}

## POC Details
- **POC File:** {poc_file}
- **Test Script:** {poc_file.with_suffix('.js')}

## Impact Assessment
TODO: Describe the impact of this vulnerability

## Steps to Reproduce
1. Deploy the target contract
2. Deploy the POC contract
3. Call the exploit() function
4. Observe the results

## Mitigation Recommendations
TODO: Suggest how to fix this vulnerability

## Files Included
- POC contract: `{poc_file.name}`
- Test script: `{poc_file.with_suffix('.js').name}`
- This report

---
*Generated by KANA Immunefi Worker*
"""

        with open(report_file, 'w') as f:
            f.write(report_content)

        print(f"[+] Submission report created: {report_file}")
        return report_file

    def execute_bounty_task(self, bounty_url):
        """Execute a complete bounty hunting task"""
        print(f"\n=== 🎯 EXECUTING BOUNTY TASK ===")
        print(f"[*] Target: {bounty_url}\n")

        # Step 1: Analyze bounty
        requirements, error = self.analyze_bounty_requirements(bounty_url)
        if error:
            print(f"[!] {error}")
            return False

        print(f"[+] Analyzed: {requirements['title']}")
        print(f"[+] Technologies: {', '.join(requirements['technologies'])}")

        # Step 2: Generate bounty ID
        bounty_id = hashlib.md5(bounty_url.encode()).hexdigest()[:8]

        # Step 3: Create POC template
        poc_file = self.create_poc_template(bounty_id, requirements)

        # Step 4: Create test script
        test_file = self.create_test_script(bounty_id, poc_file)

        # Step 5: Create submission report
        description = f"POC for {requirements['title']} - Automated generation by KANA Immunefi Worker"
        report_file = self.submit_bounty_report(bounty_id, poc_file, description)

        print(f"\n[+] Bounty task completed!")
        print(f"   POC: {poc_file}")
        print(f"   Test: {test_file}")
        print(f"   Report: {report_file}")

        return True

    def interactive_immunefi_worker(self):
        """Interactive Immunefi worker"""
        print("\n=== 🐛 IMMUNEFI BUG BOUNTY WORKER ===")
        print("[*] Automated bug hunting and POC creation\n")

        while True:
            print("[1] Scrape active bounties")
            print("[2] Analyze bounty requirements")
            print("[3] Create POC for bounty")
            print("[4] Execute complete bounty task")
            print("[5] View active bounties")
            print("[6] View submissions")
            print("[0] Exit\n")

            choice = input("[?] Select: ").strip()

            if choice == '1':
                bounties, error = self.scrape_immunefi_bounties()
                if error:
                    print(f"[!] {error}")

            elif choice == '2':
                url = input("[?] Bounty URL: ").strip()
                requirements, error = self.analyze_bounty_requirements(url)
                if error:
                    print(f"[!] {error}")
                else:
                    print(f"\n[+] Title: {requirements['title']}")
                    print(f"[+] Technologies: {', '.join(requirements['technologies'])}")
                    if requirements['scope']:
                        print(f"[+] In Scope: {len(requirements['scope'])} items")

            elif choice == '3':
                bounty_id = input("[?] Bounty ID: ").strip()
                url = input("[?] Bounty URL: ").strip()

                requirements = {
                    "title": "Manual Bounty",
                    "url": url
                }

                poc_file = self.create_poc_template(bounty_id, requirements)
                test_file = self.create_test_script(bounty_id, poc_file)

            elif choice == '4':
                url = input("[?] Bounty URL: ").strip()
                success = self.execute_bounty_task(url)
                if success:
                    print("[+] Task completed successfully!")
                else:
                    print("[!] Task failed")

            elif choice == '5':
                if self.bounties["bounties"]:
                    print(f"\n[+] Active Bounties ({len(self.bounties['bounties'])}):")
                    for bounty in self.bounties["bounties"][-10:]:  # Last 10
                        print(f"   {bounty['id']}: {bounty['title']} - {bounty['reward']}")
                else:
                    print("[!] No active bounties found")

            elif choice == '6':
                if self.bounties["submissions"]:
                    print(f"\n[+] Submissions ({len(self.bounties['submissions'])}):")
                    for sub in self.bounties["submissions"][-5:]:  # Last 5
                        print(f"   {sub['bounty_id']}: {sub['status']} - {sub['created_at'][:10]}")
                else:
                    print("[!] No submissions found")

            elif choice == '0':
                break


if __name__ == "__main__":
    worker = ImmunefiWorker()
    worker.interactive_immunefi_worker()
