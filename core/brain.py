import requests
import subprocess
import os

class KanaBrain:
    def __init__(self):
        self.url = "http://localhost:6969/v1/chat/completions"

    def ask_ai(self, prompt):
        # System Instruction agar AI memberikan output perintah yang bersih jika diminta eksekusi
        system_msg = "Kamu adalah KANA CORE. Jika user meminta eksekusi atau menjalankan perintah, berikan perintah PowerShell-nya saja di dalam blok kode."
        
        payload = {
            "model": "gemini-3.0-pro",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            r = requests.post(self.url, json=payload, timeout=60)
            return r.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_command(self, command):
        """Fungsi untuk mengeksekusi perintah di PowerShell"""
        try:
            print(f"[*] Executing: {command}")
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
            if result.returncode == 0:
                return f"[SUCCESS]\n{result.stdout}"
            else:
                return f"[FAILED]\n{result.stderr}"
        except Exception as e:
            return f"[ERROR] {str(e)}"
