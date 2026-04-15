# RESEARCH DATA: GitHub_-_pcaversaccio-white-hat-frontrunning:_White_hat_frontrunning_script_to_outpace_hackers_and_secure_funds_from_compromised_wallets._·_GitHub
SOURCE URL: https://github.com/pcaversaccio/white-hat-frontrunning
DATE: Thu Apr 16 04:18:18 2026
--------------------------------------------------

Skip to content
Navigation Menu
Sign in
Appearance settings
Appearance settings
Dismiss alert
pcaversaccio
/
white-hat-frontrunning
Public
You must be signed in to change notification settings
Code
Issues
Pull requests
Discussions
Actions
Projects
Additional navigation options
pcaversaccio/white-hat-frontrunning
 main
Go to file
Code
Folders and files
Name Last commit message Last commit date
Latest commit
3 people
🔥 Add Script Templates for zkPass and StandX Rescues (#12
last week
4504d8c
 · last week
Apr 8, 2026
History
.github/workflows
👷 Update actions/checkout GitHub Action to Version
5 months agoNov 24, 2025
community-examples
🔥 Add Script Templates for zkPass and StandX Rescues (
last weekApr 8, 2026
.env.example
🔥 Add EIP-7702 Rescue (#9)
11 months agoJun 3, 2025
.gitignore
🔥 Add EIP-7702 Rescue (#9)
11 months agoJun 3, 2025
LICENSE
🔥 For all of you scumbags - I will always be watching you!
2 years agoOct 13, 2024
README.md
📝 Fix Typo
2 months agoFeb 8, 2026
encode_recover_multicall.sh
📝 Wording
10 months agoJun 4, 2025
go.sh
📝 Update Foundry Links
2 months agoFeb 8, 2026
go_eip7702.sh
♻️ Amend Docs on Debug Mode and Add sleep 20 to
7 months agoSep 12, 2025
recoverooor.vy
🔥 Add EIP-7702 Rescue (#9)
11 months agoJun 3, 2025
Repository files navigation
README
AGPL-3.0 license
🥷🏽 White Hat Frontrunning
White hat frontrunning script to outpace hackers and secure funds from compromised wallets. The (Bash) script is intentionally designed with minimal dependencies, requiring only the native tools provided by Linux and cast from Foundry.
Usage
Note
Ensure that cast is installed locally. For installation instructions, refer to this guide.
First, modify the main loop in the script. At present, it's set to send gas to a victim wallet and transfer a specific token. Since the main loop needs to be tailored for each rescue, please review and adjust it carefully.
Next, make the script executable:
chmod +x go.sh
Tip
The script is already set as executable in the repository, so you can run it immediately after cloning or pulling the repository without needing to change permissions.
Now it's time to configure the .env accordingly (this is an illustrative .env file):
Caution
The private keys below are placeholders and should never be used in a production environment!
PROVIDER_URL="https://rpc.flashbots.net"
RELAY_URL="https://relay.flashbots.net"
VICTIM_PK="0x1234567890"
GAS_PK="0x9876543210"
FLASHBOTS_SIGNATURE_PK="0x31337"
TOKEN_CONTRACT="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
Tip
When submitting bundles to Flashbots, they are signed with your FLASHBOTS_SIGNATURE_PK key, enabling Flashbots to verify your identity and track your reputation over time. This reputation system is designed to safeguard the infrastructure from threats such as DDoS attacks. It's important to note that this key does not handle any funds and is not required to be the primary Ethereum key used for transaction authentication. Its sole purpose is to establish your identity with Flashbots. You can use any ECDSA secp256k1 key for this, and if you need to create a new one, you can use cast wallet new.
Finally, execute the script:
./go.sh
To enable debug mode, set the DEBUG environment variable to true before running the script:
DEBUG=true ./go.sh
This will print each command before it is executed, which is helpful when troubleshooting.
Warning
The debug mode is not a dry-run. It will still send the rescue transactions, only with extra output.
EIP-7702-Based Rescue
Using EIP-7702, you can rescue all funds from a compromised wallet using a paymaster and a friendly delegator. There is no need to send ether to the compromised wallet at all. The script go_eip7702.sh handles the full rescue logic. It deploys a Vyper contract called recoverooor.vy, which acts as the (friendly) delegator to facilitate the asset transfers. All you need to do is set the environment variables RPC_URL, VICTIM_PK, and PAYMASTER_PK, along with the PAYLOAD parameter containing the calldata to be executed by the delegator contract.
Tip
To generate the same bytecode for recoverooor.vy as the script go_eip7702.sh, install the necessary dependencies via pip install vyper==0.4.2 snekmate==0.1.2rc1 and compile the contract using vyper recoverooor.vy.
To get started, configure your .env file as shown below:
Caution
The private keys below are placeholders and should never be used in a production environment!
RPC_URL="https://rpc.flashbots.net"
VICTIM_PK="0x1234567890"
PAYMASTER_PK="0xba5Ed"
The PAYLOAD parameter in the script go_eip7702.sh must be the calldata that calls the recoverooor.vy contract with the appropriate logic (refer to the encode_recover_multicall.sh script for details on how to encode calldata for the recover_multicall function). The recoverooor.vy contract will be deployed with the paymaster wallet as the OWNER. The script also resets the EIP-7702 authorisation at the end, in case the OWNER can no longer be trusted in the future.
To perform the rescue, simply run:
./go_eip7702.sh
To enable debug mode, set the DEBUG environment variable to true before running the script:
DEBUG=true ./go_eip7702.sh
This will print each command before it is executed, which is helpful when troubleshooting.
Warning
The debug mode is not a dry-run. It will still send the rescue transactions, only with extra output.
Tip
To make an authorisation replayable across all chains, simply set the chain ID to 0 (see here). While cast does not currently support this feature, you can use my ethers-based script to generate a replayable authorisation. This authorisation can then be passed into the main script.
Community Examples
Warning
I have reviewed these examples as part of the PR process, but they haven't been fully tested. Please ensure a thorough review before using them!
The community-examples/ directory contains customised versions of the primary go.sh script, tailored for a variety of rescue scenarios.
Real-World Rescues
Degen Rescue
Zyfai Rescue
Contributors
5
Languages
Shell
90.1%
Vyper
9.9%
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information