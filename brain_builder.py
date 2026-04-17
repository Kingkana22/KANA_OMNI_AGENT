import os
import json
import glob
from datetime import datetime

class KanaBrainBuilder:
    def __init__(self):
        self.kb_dir = "knowledge_base/reference_codes"
        self.brain_file = "knowledge_base/brain_data.json"
        self.memory = {
            "patterns": [],
            "rules": [],
            "last_learned": ""
        }

    def learn_from_chat(self):
        """Menyimpan logika instruksi chat manual (Hardcoded Rules)"""
        print("[*] Mengingat instruksi chat...")
        rules = [
            "Cari fungsi withdraw tanpa onlyowner",
            "Identifikasi delegatecall ke address eksternal",
            "Pantau pola reentrancy pada fungsi payable",
            "Pastikan bot beroperasi dengan 8 workers untuk speed optimal"
        ]
        self.memory["rules"] = rules

    def learn_from_repos(self):
        """Membaca ribuan baris kode Solidity dari hasil scraping"""
        print("[*] Membedah kode dari repository...")
        # Mencari semua file .sol di folder knowledge_base
        sol_files = glob.glob(f"{self.kb_dir}/**/*.sol", recursive=True)
        
        count = 0
        for file_path in sol_files[:500]: # Limit 500 file agar tidak terlalu berat
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Ekstrak nama fungsi yang berpotensi bahaya
                    if "function" in content:
                        count += 1
                        self.memory["patterns"].append({
                            "source": os.path.basename(file_path),
                            "keywords": [w for w in ["withdraw", "transfer", "call", "delegate"] if w in content.lower()]
                        })
            except: continue
        print(f"[+] Berhasil mempelajari {count} pola dari kode Solidity.")

    def save_brain(self):
        self.memory["last_learned"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.brain_file, 'w') as f:
            json.dump(self.memory, f, indent=4)
        print(f"[!] Brain Data diperbarui: {self.brain_file}")

    def sync_brain(self):
        print("[*] Mengirim kecerdasan ke Cloud...")
        # Hanya commit file otak yang dihasilkan dan hindari force push
        os.system(f"git add {self.brain_file} && git commit -m 'AI_Brain_Sync' && git push origin main")

    def run(self):
        print("=== 🧠 KANA AI LEARNING MODE ACTIVE ===")
        self.learn_from_chat()
        self.learn_from_repos()
        self.save_brain()
        self.sync_brain()
        print("=== ✅ AI SELESAI BELAJAR ===")

if __name__ == "__main__":
    KanaBrainBuilder().run()