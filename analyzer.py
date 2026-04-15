import os

class KanaAnalyzer:
    def __init__(self):
        self.kb_path = "knowledge_base"
        # Daftar kata kunci yang menandakan "Cuan" atau "Bahaya"
        self.targets = ["vulnerability", "exploit", "critical", "bug bounty", "bypass", "reentrancy", "flash loan"]

    def scan_knowledge(self):
        print(f"\n{'='*40}")
        print("   KANA CORE: KNOWLEDGE ANALYZER")
        print(f"{'='*40}")
        
        found_count = 0
        files = [f for f in os.listdir(self.kb_path) if f.endswith('.md')]
        
        for file in files:
            path = os.path.join(self.kb_path, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
                # Cek apakah ada kata kunci di dalam file
                found_keywords = [word for word in self.targets if word in content]
                
                if found_keywords:
                    print(f"\n[!] POTENSI DITEMUKAN: {file}")
                    print(f"    Keywords: {', '.join(found_keywords)}")
                    found_count += 1
        
        if found_count == 0:
            print("\n[○] Tidak ada temuan kritis dari dataset saat ini.")
        else:
            print(f"\n[✔] Total {found_count} file berisi informasi sensitif.")

if __name__ == "__main__":
    scanner = KanaAnalyzer()
    scanner.scan_knowledge()