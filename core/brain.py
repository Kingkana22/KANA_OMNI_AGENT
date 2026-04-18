import requests

class KanaBrain:
    def __init__(self):
        # Alamat API dari WebAI-to-API Anda
        self.url = "http://localhost:6969/v1/chat/completions"

    def ask_ai(self, prompt):
        payload = {
            "model": "gemini-pro",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            r = requests.post(self.url, json=payload, timeout=60)
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content']
            else:
                return f"Error: Server response {r.status_code}"
        except Exception as e:
            return f"Connection Error: Pastikan server di port 6969 aktif! ({str(e)})"
