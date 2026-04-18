# RESEARCH DATA: GitHub_-_SunWeb3Sec-DeFiHackLabs:_Reproduce_DeFi_hacked_incidents_using_Foundry._·_GitHub
SOURCE URL: https://github.com/SunWeb3Sec/DeFiHackLabs
DATE: Thu Apr 16 04:25:14 2026
--------------------------------------------------

Skip to content
Navigation Menu
Sign in
Appearance settings
Appearance settings
Dismiss alert
SunWeb3Sec
/
DeFiHackLabs
Public
You must be signed in to change notification settings
Code
Issues
Pull requests
4
Discussions
Actions
Projects
Additional navigation options
SunWeb3Sec/DeFiHackLabs
 main
Go to file
Code
Folders and files
Name Last commit message Last commit date
Latest commit
SunWeb3Sec
Merge pull request #1033 from coolestowl/main
5 days ago
e2cc0be
 · 5 days ago
Apr 11, 2026
History
.github
github: add forge fmt before build
2 years agoNov 4, 2024
academy
Add Japanese for OnChain Transaction Debugging: 7
11 months agoJun 2, 2025
lib
Revert "POC for DRLVAULTV3"
4 months agoDec 3, 2025
past
add parity multisig july 2017 poc
2 weeks agoMar 30, 2026
script
fix: dont run the template when running a poc
7 months agoSep 16, 2025
src
feat: add EST Token incorrect token burn mechanism PoC (20260327)
5 days agoApr 11, 2026
.gitignore
feat: add Kame exploit and misc additions
7 months agoSep 16, 2025
.gitmodules
Revert "POC for DRLVAULTV3"
4 months agoDec 3, 2025
.prettierrc
chore: add prettierrc
2 years agoApr 27, 2024
AudiusPocGasReport.gif
Add demo gif of producing gas report for the audius poc
4 years agoAug 18, 2022
7 months ago
5 days ago
7 months ago
8 months ago
7 months ago
3 years ago
7 months ago
11 months ago
View all files
Repository files navigation
README
Contributing
DeFi Hacks Reproduce - Foundry
Reproduce DeFi hack incidents using Foundry.
689 incidents included.
Let's make Web3 secure! Join Discord
Notion: 101 root cause analysis of past DeFi hacked incidents
Transaction debugging tools
Disclaimer: This content serves solely as a proof of concept showcasing past DeFi hacking incidents. It is strictly intended for educational purposes and should not be interpreted as encouraging or endorsing any form of illegal activities or actual hacking attempts. The provided information is for informational and learning purposes only, and any actions taken based on this content are solely the responsibility of the individual. The usage of this information should adhere to applicable laws, regulations, and ethical standards.
Table of Contents
Getting Started
Who Support Us
Donate Us
List of Past DeFi Incidents
Transaction debugging tools
Ethereum Signature Database
Useful tools
Hacks Dashboard
List of DeFi Hacks & POCs
Getting Started
Follow the instructions to install Foundry.
Clone and install dependencies:git submodule update --init --recursive
Contributing Guidelines
Web3 Cybersecurity Academy
All articles are also published on Substack.
OnChain transaction debugging
Lesson 1: Tools ( English | 中文 | Vietnamese | Korean | Spanish | 日本語 )
Lesson 2: Warm up ( English | 中文 | Korean | Spanish | 日本語 )
Lesson 3: Write Your Own PoC (Price Oracle Manipulation) ( English | 中文 | Korean | Spanish | 日本語 )
Lesson 4: Write Your Own PoC (MEV Bot) ( English | 中文 | Korean | Spanish | 日本語 )
Lesson 5: Rugpull Analysis ( English | 中文 | Spanish | 日本語 )
Lesson 6: Write Your Own PoC (Reentrancy) ( English | 中文 | Spanish | 日本語 )
Lesson 7: Hack Analysis: Nomad Bridge, August 2022 ( English | 中文 | Spanish | 日本語 )
Donate us
If you appreciate our work, please consider donating. Even a small amount helps us continue developing and improving our projects, and promoting web3 security.
Gitcoin - Donate DeFiHackLabs
EVM Chains - 0xD7d6215b4EF4b9B5f40baea48F41047Eb67a11D5
Giveth
List of Past DeFi Incidents
20260327 EST Token
20260310 AlkemiEarn
20260315 Venus THE
20260302 Curve LlamaLend
20260222 LAXO Token
20260215 Moonwell
20260120 Makina
20260120 SynapLogic
20260112 MTToken
20260110 FutureSwap
20260109 TRU
20260101 PRXVT
2025
2024
2023
2022
2021
Before 2020
Transaction debugging tools
Phalcon | Tx tracer | Cruise | Ethtx | Tenderly | eigenphi
Ethereum Signature Database
4byte | sig db | etherface
Useful tools
ABI to interface | Get ABI for unverified contracts | ETH Calldata Decoder | ETHCMD - Guess ABI | Abi tools
Hacks Dashboard
Slowmist | Defillama | De.Fi | Rekt | Cryptosec | BlockSec
List of DeFi Hacks & POCs
20260327 EST Token - Incorrect Token Burn Mechanism
Lost: 150.2 WBNB
forge test --contracts src/test/2026-03/EST_exp.sol -vvv --evm-version shanghai
Contract
EST_exp.sol
Link reference
https://bscscan.com/address/0xD4524Be41cd452576aB9FF7b68a0b89aF8498a91
20260315 Venus THE - BorrowBehalf + Donation Attack
Lost: 913,858.263360521396654198 CAKE + 1,972.530910582753621682 WBNB
forge test --contracts src/test/2026-03/Venus_THE_exp.sol --match-test testTraceDrivenPoC -vvv
Contract
Venus_THE_exp.sol
Link reference
https://bscscan.com/tx/0x4f477e941c12bbf32a58dc12db7bb0cb4d31d41ff25b2457e6af3c15d7f5663f
20260310 AlkemiEarn - Business Logic
Lost: 43.45 ETH
forge test --contracts ./src/test/2026-03/AlkemiEarn_exp.sol -vvv
Contract
AlkemiEarn_exp.sol
Link reference
https://x.com/blockaid_/status/2031351881029546194
20260302 Curve LlamaLend - Share price manipulation
Lost: ~240,000 US$
forge test -vvv --contracts ./src/test/2026-03/Curve_LlamaLend_exp.sol
Contract
Curve_LlamaLend_exp.sol
Link reference
https://x.com/yieldsandmore/status/2028368378457362629
20260222 LAXO Token - Incorrect Burn Logic
Lost: ~137,000 US$
forge test src/test/2026-02/LAXO_Token_exp.sol -vvv
Contract
LAXO_Token_exp.sol
Link reference
https://x.com/CertiKAlert/status/2027317095420072317
20260215 Moonwell - Faulty Oracle
Lost: 1.78M USD
forge test --contracts ./src/test/2026-02/Moonwell_exp.sol -vvv
Contract
Moonwell_exp.sol
Link reference
https://forum.moonwell.fi/t/mip-x43-cbeth-oracle-incident-summary/2068
https://forum.moonwell.fi/t/recovery-plan-cbeth-incident-and-moonwell-apollo-onboarding/2084
https://x.com/pashov/status/2023872510077616223
https://x.com/moo9000/status/2024040101982990534
20260120 SynapLogic - Business Logic Flaw
NOTICE: SynapLogic is totally a cheat contract, with backdoors, vulnerabilities and rug pulls.
Lost: 27.6 ETH & 3450 USDC
forge test -vvv --contracts ./src/test/2026-01/SynapLogic_exp.sol
Contract
SynapLogic_exp.sol
Link reference
https://x.com/TenArmorAlert/status/2013432861366292520?s=20
https://x.com/hklst4r/status/2013440353844461979?s=20
https://x.com/CertiKAlert/status/2013440963851755610?s=20
https://x.com/nn0b0dyyy/status/2013445844394279260?s=20
20260120 Makina - Price Oracle Manipulation
Lost: 5.1M USD
forge test -vvv --contracts ./src/test/2026-01/makina_exp.sol --evm-version cancun
# MUST use evm >= cancun
Contract
makina_exp.sol
Link reference
https://x.com/nn0b0dyyy/status/2013472538832314630
https://x.com/TenArmorAlert/status/2013460083078836342
https://x.com/CertiKAlert/status/2013473512116363734
20260112 MTToken - Incorrect Fee Logic
Lost: 37K USD
forge test -vvv --contracts ./src/test/2026-01/MTToken_exp.sol
Contract
MTToken_exp.sol
Link reference
https://x.com/TenArmorAlert/status/2010630024274010460?s=20
https://x.com/nn0b0dyyy/status/2010638145155661942?s=20
20260110 FutureSwap - Unit Mismatch
Lost: 433K USD
forge test -vvv --contracts ./src/test/2026-01/futureswap_exp.sol.sol
Contract
futureswap_exp.sol
Link reference
https://x.com/nn0b0dyyy/status/2009922304927731717?s=20
20260109 Truebit - OverFlow
Lost: 8540ETH
forge test --contracts ./src/test/2026-01/Truebit_exp.sol -vvv
Contract
Truebit_exp.sol
Link reference
https://www.certik.com/zh-CN/resources/blog/truebit-incident-analysis
20260101 PRXVT - Bussiness Logic Flaw
Lost: 32.8 ETH
forge test --contracts ./src/test/2026-01/PRXVT_exp.sol -vvv --block-gas-limit 60000000 # use gas limit control iterations
Contract
PRXVT_exp.sol
Link reference
https://x.com/CertiKAlert/status/2006685174587605315
View Gas Reports
Foundry also has the ability to report the gas used per function call which mimics the behavior of hardhat-gas-reporter. Generally speaking if gas costs per function call is very high, then the likelihood of its success is reduced. Gas optimization is an important activity done by smart contract developers.
Every poc in this repository can produce a gas report like this:
forge test --gas-report --contracts <contract> -vvv
For Example: Let us find out the gas used in the Audius poc
Execution
forge test --gas-report --contracts ./src/test/Audius.exp.sol -vvv
Demo
Bug Reproduce
Moved to DeFiVulnLabs
FlashLoan Testing
Moved to DeFiLabs
Releases
No releases published
Packages
No packages published
Contributors
146
+ 132 contributors
Languages
Solidity
98.0%
Python
2.0%
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