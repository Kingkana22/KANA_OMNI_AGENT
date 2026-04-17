import os
import re

class CuanAnalyzer:
    def __init__(self):
        self.victim_dir = "cloned_repos"
        self.log_file = "logs/cuan_analysis.log"
        os.makedirs("logs", exist_ok=True)
        # Pola regex yang lebih brute untuk "lubang uang"
        self.money_leaks = {
            "REENTRANCY": re.compile(r"\.call\s*\{\s*value\s*:", re.IGNORECASE),
            "OWNER_BYPASS": re.compile(r"function\s+\w*withdraw\w*", re.IGNORECASE),  # Deteksi fungsi withdraw
            "DELEGATE_CALL": re.compile(r"delegatecall", re.IGNORECASE),
            "SELF_DESTRUCT": re.compile(r"selfdestruct", re.IGNORECASE),
            "TX_ORIGIN": re.compile(r"tx\.origin", re.IGNORECASE),
            "UNCHECKED_CALL": re.compile(r"\.call\s*\{", re.IGNORECASE),
            "INTEGER_OVERFLOW": re.compile(r"uint\d*\s*\+\s*uint\d*", re.IGNORECASE),
            "WEAK_RANDOM": re.compile(r"block\.(timestamp|number|hash)", re.IGNORECASE),
        }

    def check_owner_bypass(self, content, line_num):
        """Brute check: Jika fungsi withdraw tanpa onlyOwner dalam 5 baris sebelumnya"""
        func_match = self.money_leaks["OWNER_BYPASS"].search(content[line_num])
        if func_match:
            # Cek 5 baris sebelumnya untuk onlyOwner
            start = max(0, line_num - 5)
            for i in range(start, line_num):
                if re.search(r"onlyOwner", content[i], re.IGNORECASE):
                    return False  # Ada onlyOwner, aman
            return True  # Tidak ada, bypass potensial
        return False

    def analyze(self):
        print("[*] BRUTE ANALYZING CLONED REPOS FOR MONEY LEAKS...")
        if not os.path.exists(self.victim_dir):
            print(f"[!] Direktori {self.victim_dir} tidak ada. Buat dulu!")
            return

        found_cuan = {}
        total_files = 0

        with open(self.log_file, "w", encoding="utf-8") as log:
            log.write("=== CUAN ANALYSIS REPORT ===\n")

            for root, dirs, files in os.walk(self.victim_dir):
                for file in files:
                    if file.endswith(".sol"):
                        path = os.path.join(root, file)
                        total_files += 1
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                content = f.readlines()
                                for line_num, line in enumerate(content):
                                    # Skip komentar
                                    if line.strip().startswith("//") or "/*" in line:
                                        continue
                                    for bug_name, pattern in self.money_leaks.items():
                                        if bug_name == "OWNER_BYPASS":
                                            if self.check_owner_bypass(content, line_num):
                                                msg = f"💰 [POTENSI CUAN] {bug_name} found in {file} (Line {line_num + 1})\n   Context: {line.strip()}"
                                                print(msg)
                                                log.write(msg + "\n")
                                                found_cuan[bug_name] = found_cuan.get(bug_name, 0) + 1
                                        elif pattern.search(line):
                                            msg = f"💰 [POTENSI CUAN] {bug_name} found in {file} (Line {line_num + 1})\n   Context: {line.strip()}"
                                            print(msg)
                                            log.write(msg + "\n")
                                            found_cuan[bug_name] = found_cuan.get(bug_name, 0) + 1
                        except Exception as e:
                            print(f"[!] Error reading {path}: {e}")
                            continue

            # Summary
            log.write(f"\n=== SUMMARY ===\nTotal files analyzed: {total_files}\n")
            for bug, count in found_cuan.items():
                log.write(f"{bug}: {count} instances\n")
            if not found_cuan:
                msg = "[!] Belum ada celah kritis. Terus kumpulkan target di KB."
                print(msg)
                log.write(msg + "\n")
            else:
                print(f"[+] Analysis complete. Check {self.log_file} for details.")

if __name__ == "__main__":
    CuanAnalyzer().analyze()