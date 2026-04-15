import os

class CuanAnalyzer:
    def __init__(self):
        self.victim_dir = "cloned_repos"
        # Pola kode yang merupakan "lubang uang"
        self.money_leaks = {
            "REENTRANCY": ".call{value: ",
            "OWNER_BYPASS": "onlyOwner", # Cek apakah ada fungsi withdraw tanpa ini
            "DELEGATE_CALL": "delegatecall",
            "SELF_DESTRUCT": "selfdestruct",
            "TX_ORIGIN": "tx.origin"
        }

    def analyze(self):
        print("[*] ANALYZING CLONED REPOS FOR MONEY LEAKS...")
        found_cuan = False
        
        for root, dirs, files in os.walk(self.victim_dir):
            for file in files:
                if file.endswith(".sol"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.readlines()
                            for line_num, line in enumerate(content):
                                for bug_name, pattern in self.money_leaks.items():
                                    if pattern in line:
                                        print(f"💰 [POTENSI CUAN] {bug_name} found in {file} (Line {line_num})")
                                        print(f"   Context: {line.strip()}")
                                        found_cuan = True
                    except: continue
        
        if not found_cuan:
            print("[!] Belum ada celah kritis. Terus kumpulkan target di KB.")

if __name__ == "__main__":
    CuanAnalyzer().analyze()