"""KANA Omni Agent v2 - modular CLI agent.

Tujuan refactor:
- Struktur modular (config, client AI, tools filesystem, orchestrator CLI).
- Lebih aman untuk operasi file lokal (anti path traversal).
- Mudah di-extend (register tool baru via ToolRegistry).
"""

from __future__ import annotations

import logging
import os
import shlex
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, List

from dotenv import load_dotenv
from openai import OpenAI


# -------------------------------
# Configuration
# -------------------------------


@dataclass(frozen=True)
class AgentConfig:
    proxy_url: str
    proxy_key: str
    model_gemini: str
    model_codex: str
    temperature: float = 0.2
    workspace_dir: Path = Path("./workspace")
    memory_file: Path = Path("./workspace/chat_history.json")
    max_history_messages: int = 30
    system_prompt: str = (
        "Kamu adalah KANA CORE, AI assistant yang membantu user secara aman, "
        "ringkas, dan actionable. Kamu berjalan di lingkungan lokal dengan akses "
        "ke folder workspace melalui tools internal agent."
    )

    @staticmethod
    def from_env() -> "AgentConfig":
        load_dotenv()

        proxy_url = os.getenv("PROXY_URL", "").strip()
        proxy_key = os.getenv("PROXY_KEY", "").strip()
        model_gemini = os.getenv("MODEL_GEMINI", "").strip()
        model_codex = os.getenv("MODEL_CODEX", "").strip()

        missing = [
            key
            for key, value in {
                "PROXY_URL": proxy_url,
                "PROXY_KEY": proxy_key,
                "MODEL_GEMINI": model_gemini,
                "MODEL_CODEX": model_codex,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Env belum lengkap: {', '.join(missing)}")

        return AgentConfig(
            proxy_url=proxy_url,
            proxy_key=proxy_key,
            model_gemini=model_gemini,
            model_codex=model_codex,
        )


# -------------------------------
# AI client + model routing
# -------------------------------


class ModelRouter:
    def __init__(self, config: AgentConfig) -> None:
        self._models = {
            "gemini": config.model_gemini,
            "codex": config.model_codex,
        }

    def resolve(self, model_type: str) -> str:
        key = model_type.lower().strip()
        if key not in self._models:
            available = ", ".join(sorted(self._models))
            raise ValueError(f"Model '{model_type}' tidak tersedia. Pilihan: {available}")
        return self._models[key]


class AIClient:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.router = ModelRouter(config)
        self.client = OpenAI(base_url=config.proxy_url, api_key=config.proxy_key)

    def execute_task(
        self,
        prompt: str,
        model_type: str = "gemini",
        history: Optional[List[dict]] = None,
        behavior_rules: Optional[List[str]] = None,
    ) -> str:
        model = self.router.resolve(model_type)
        system_prompt = self.config.system_prompt
        if behavior_rules:
            joined = "\n".join(f"- {rule}" for rule in behavior_rules)
            system_prompt = f"{system_prompt}\n\nAturan tambahan dari user:\n{joined}"

        messages: List[dict] = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.config.temperature,
            )
            return response.choices[0].message.content or "(Tidak ada respons)"
        except Exception as exc:  # nosec - network/API exception expected
            logging.exception("Koneksi API gagal")
            return f"ERROR KONEKSI: {exc}"

    def plan_workspace_action(
        self,
        user_input: str,
        model_type: str = "gemini",
        behavior_rules: Optional[List[str]] = None,
    ) -> Optional[dict]:
        """
        Minta model menentukan apakah user meminta aksi workspace.
        Return dict action jika valid, contoh:
        {"action":"create_file","path":"a.txt","content":"hello"}
        """
        model = self.router.resolve(model_type)
        system_prompt = (
            "Kamu adalah planner aksi tools. "
            "Analisa input user dan keluarkan JSON saja tanpa markdown. "
            "Jika butuh aksi workspace, pakai salah satu action: "
            "create_file, create_folder, read_file, list_workspace. "
            "Kalau bukan aksi workspace, keluarkan {\"action\":\"none\"}."
        )
        if behavior_rules:
            joined = "\n".join(f"- {rule}" for rule in behavior_rules)
            system_prompt = f"{system_prompt}\nAturan tambahan user:\n{joined}"

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.0,
            )
            raw = response.choices[0].message.content or ""
            parsed = self._extract_json(raw)
            if not parsed:
                return None
            if parsed.get("action") == "none":
                return None
            return parsed
        except Exception:
            logging.exception("Planner aksi gagal")
            return None

    @staticmethod
    def _extract_json(raw: str) -> Optional[dict]:
        raw = raw.strip()
        if not raw:
            return None
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else None
        except Exception:
            # fallback: ambil objek JSON pertama di text
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if not match:
                return None
            try:
                data = json.loads(match.group(0))
                return data if isinstance(data, dict) else None
            except Exception:
                return None


# -------------------------------
# Tools: filesystem
# -------------------------------


class WorkspaceTool:
    def __init__(self, workspace_dir: Path) -> None:
        self.workspace_dir = workspace_dir
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, filename: str) -> Path:
        target = (self.workspace_dir / filename).resolve()
        workspace_resolved = self.workspace_dir.resolve()

        if workspace_resolved not in target.parents and target != workspace_resolved:
            raise ValueError("Path tidak valid (di luar workspace)")
        return target

    def create_file(self, filename: str, content: str) -> str:
        try:
            safe_target = self._safe_path(filename)
            safe_target.parent.mkdir(parents=True, exist_ok=True)
            safe_target.write_text(content, encoding="utf-8")
            rel = safe_target.relative_to(self.workspace_dir.resolve())
            return f"BERHASIL: File '{rel}' dibuat di folder workspace."
        except Exception as exc:
            return f"GAGAL: {exc}"

    def create_folder(self, foldername: str) -> str:
        try:
            safe_target = self._safe_path(foldername)
            safe_target.mkdir(parents=True, exist_ok=True)
            rel = safe_target.relative_to(self.workspace_dir.resolve())
            return f"BERHASIL: Folder '{rel}/' siap digunakan."
        except Exception as exc:
            return f"GAGAL: {exc}"

    def read_file(self, filename: str) -> str:
        try:
            safe_target = self._safe_path(filename)
            if not safe_target.exists():
                return f"GAGAL: File '{filename}' tidak ditemukan."
            if safe_target.is_dir():
                return f"GAGAL: '{filename}' adalah folder, bukan file."
            data = safe_target.read_text(encoding="utf-8")
            return data if data else "(File kosong)"
        except Exception as exc:
            return f"GAGAL: {exc}"

    def list_workspace(self) -> str:
        try:
            base = self.workspace_dir.resolve()
            entries = sorted(base.rglob("*"))
            if not entries:
                return "(workspace kosong)"

            lines: List[str] = []
            for item in entries:
                rel = item.relative_to(base)
                suffix = "/" if item.is_dir() else ""
                lines.append(f"- {rel}{suffix}")
            return "\n".join(lines)
        except Exception as exc:
            return f"GAGAL: {exc}"


# -------------------------------
# Command registry and parser
# -------------------------------


CommandHandler = Callable[[str], str]


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: Dict[str, CommandHandler] = {}

    def register(self, name: str, handler: CommandHandler) -> None:
        self._handlers[name] = handler

    def handle(self, command: str, payload: str) -> Optional[str]:
        handler = self._handlers.get(command)
        if not handler:
            return None
        return handler(payload)


class KanaOmniAgent:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.ai_client = AIClient(config)
        self.workspace = WorkspaceTool(config.workspace_dir)
        self.registry = ToolRegistry()
        self.active_model = "gemini"
        self.history: List[dict] = self._load_history()
        self.behavior_rules: List[str] = []

        self.registry.register("file", self._handle_file_command)
        self.registry.register("read", self._handle_read_command)
        self.registry.register("ls", self._handle_ls_command)
        self.registry.register("model", self._handle_model_command)
        self.registry.register("history", self._handle_history_command)
        self.registry.register("help", self._handle_help_command)
        self.registry.register("rule", self._handle_rule_command)
        self.registry.register("rules", self._handle_rules_command)
        self.registry.register("reset_rules", self._handle_reset_rules_command)

    def _load_history(self) -> List[dict]:
        self.config.memory_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.config.memory_file.exists():
            return []
        try:
            raw = self.config.memory_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, list):
                return [m for m in data if isinstance(m, dict) and "role" in m and "content" in m]
            return []
        except Exception:
            logging.warning("Gagal memuat history. Memulai sesi baru.")
            return []

    def _save_history(self) -> None:
        trimmed = self.history[-self.config.max_history_messages :]
        self.config.memory_file.write_text(
            json.dumps(trimmed, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _handle_file_command(self, payload: str) -> str:
        # format: /file <filename> :: <content>
        if "::" not in payload:
            return "Format salah. Gunakan: /file <filename> :: <content>"

        filename_raw, content = payload.split("::", 1)
        filename = filename_raw.strip()
        if not filename:
            return "Nama file tidak boleh kosong."
        return self.workspace.create_file(filename=filename, content=content.strip())

    def _handle_model_command(self, payload: str) -> str:
        model_type = payload.strip().lower()
        self.ai_client.router.resolve(model_type)
        self.active_model = model_type
        return f"Model aktif: {self.active_model}"

    def _handle_read_command(self, payload: str) -> str:
        filename = self._normalize_file_reference(payload)
        if not filename:
            return "Format salah. Gunakan: /read <filename>"
        return self.workspace.read_file(filename)

    def _handle_ls_command(self, payload: str) -> str:
        _ = payload
        return self.workspace.list_workspace()

    def _handle_history_command(self, payload: str) -> str:
        _ = payload
        if not self.history:
            return "(history kosong)"
        preview = self.history[-10:]
        lines = [f"{idx+1}. [{m.get('role')}] {m.get('content')}" for idx, m in enumerate(preview)]
        return "\n".join(lines)

    def _handle_help_command(self, payload: str) -> str:
        _ = payload
        return (
            "Tips cepat:\n"
            "- Cukup ketik natural: 'buat file app.py isi print(\"halo\")'\n"
            "- 'buat folder data/raw'\n"
            "- 'baca file app.py'\n"
            "- 'lihat dan list isi folder ku'\n"
            "- Atur perilaku AI via chat: 'ingat aturan: jawab singkat'\n"
            "- Slash command opsional: /model, /ls, /read, /file, /history, /help, /rule, /rules, /reset_rules"
        )

    def _handle_rule_command(self, payload: str) -> str:
        rule = payload.strip()
        if not rule:
            return "Format: /rule <aturan_baru>"
        self.behavior_rules.append(rule)
        return f"Aturan ditambahkan ({len(self.behavior_rules)}): {rule}"

    def _handle_rules_command(self, payload: str) -> str:
        _ = payload
        if not self.behavior_rules:
            return "(belum ada aturan tambahan)"
        return "\n".join(f"{idx+1}. {rule}" for idx, rule in enumerate(self.behavior_rules))

    def _handle_reset_rules_command(self, payload: str) -> str:
        _ = payload
        self.behavior_rules.clear()
        return "Semua aturan tambahan direset."

    def _handle_behavior_rule_from_chat(self, user_input: str) -> Optional[str]:
        patterns = [
            r"^(?:ingat|catat)\s+aturan\s*:\s*(.+)$",
            r"^(?:mulai sekarang|sekarang)\s+aturan(?:nya)?\s*:\s*(.+)$",
        ]
        for pattern in patterns:
            m = re.search(pattern, user_input.strip(), flags=re.IGNORECASE | re.DOTALL)
            if m:
                rule = m.group(1).strip()
                if rule:
                    self.behavior_rules.append(rule)
                    return f"Siap. Aturan baru disimpan: {rule}"
        return None

    @staticmethod
    def _normalize_file_reference(text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"^(?:file|berkas)\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+(?:file|berkas)$", "", cleaned, flags=re.IGNORECASE)
        parts = cleaned.split()
        if not parts:
            return ""
        # ambil token pertama untuk kasus '/read main.py file'
        return parts[0].strip()

    @staticmethod
    def _extract_file_create_intent(text: str) -> Optional[tuple[str, str]]:
        """
        Contoh yang didukung:
        - buat file app.py isi print("halo")
        - create file app.py: print("halo")
        - tulis file notes/todo.txt -> belanja
        """
        patterns = [
            r"(?:buat|buatkan|create|tulis)\s+file\s+([^\s:]+)\s*(?:isi|content|:|->)\s+(.+)",
            r"(?:save|simpan)\s+ke\s+file\s+([^\s:]+)\s*(?:isi|content|:|->)\s+(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip(), match.group(2).strip()
        return None

    @staticmethod
    def _extract_folder_create_intent(text: str) -> Optional[str]:
        patterns = [
            r"(?:buat|buatkan|create)\s+folder\s+([^\s]+)",
            r"(?:buat|buatkan|create)\s+direktori\s+([^\s]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _extract_read_intent(text: str) -> Optional[str]:
        patterns = [
            r"(?:baca|read|lihat)\s+file\s+([^\s]+)",
            r"(?:open)\s+([^\s]+\.[A-Za-z0-9]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return KanaOmniAgent._normalize_file_reference(match.group(1).strip())
        return None

    @staticmethod
    def _is_list_intent(text: str) -> bool:
        lowered = text.lower()
        if lowered.strip() in {"ls", "dir"}:
            return True

        list_words = {"lihat", "list", "daftar", "tampilkan", "show"}
        target_words = {"folder", "file", "isi", "directory", "direktori"}
        has_list_word = any(w in lowered for w in list_words)
        has_target_word = any(w in lowered for w in target_words)
        return has_list_word and has_target_word

    def _try_natural_tool_action(self, user_input: str) -> Optional[str]:
        folder_name = self._extract_folder_create_intent(user_input)
        if folder_name:
            return self.workspace.create_folder(folder_name)

        file_intent = self._extract_file_create_intent(user_input)
        if file_intent:
            filename, content = file_intent
            return self.workspace.create_file(filename=filename, content=content)

        read_file = self._extract_read_intent(user_input)
        if read_file:
            return self.workspace.read_file(read_file)

        if self._is_list_intent(user_input):
            return self.workspace.list_workspace()

        return None

    def _execute_planned_workspace_action(self, plan: dict) -> Optional[str]:
        action = str(plan.get("action", "")).strip().lower()
        path = str(plan.get("path", "")).strip()
        content = str(plan.get("content", ""))

        if action == "create_file" and path:
            return self.workspace.create_file(path, content)
        if action == "create_folder" and path:
            return self.workspace.create_folder(path)
        if action == "read_file" and path:
            return self.workspace.read_file(path)
        if action == "list_workspace":
            return self.workspace.list_workspace()
        return None

    @staticmethod
    def _parse_slash_command(raw: str) -> tuple[Optional[str], str]:
        if not raw.startswith("/"):
            return None, raw

        try:
            parts = shlex.split(raw)
        except ValueError:
            # fallback jika quote user tidak balance
            parts = raw.split(maxsplit=1)

        if not parts:
            return None, raw

        command_name = parts[0].lstrip("/").strip().lower()
        payload = raw[len(parts[0]) :].strip()
        return command_name, payload

    def run(self) -> None:
        print("=" * 56)
        print(" KANA OMNI AGENT • Professional Console ".center(56, "="))
        print("=" * 56)
        print(f"Proxy  : {self.config.proxy_url}")
        print(f"Model  : {self.active_model}")
        print("Mode   : Chat-first (AI planner + optional slash commands)")
        print("Ketik 'help' atau '/help' untuk bantuan. Ketik 'exit' untuk keluar.")

        while True:
            user_input = input("\nMasukan Perintah (atau 'exit'): ").strip()
            if user_input.lower() == "exit":
                self._save_history()
                print("Sesi selesai.")
                break

            if user_input.lower() == "help":
                print(self._handle_help_command(""))
                continue

            behavior_ack = self._handle_behavior_rule_from_chat(user_input)
            if behavior_ack is not None:
                print(behavior_ack)
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": behavior_ack})
                continue

            cmd, payload = self._parse_slash_command(user_input)
            if cmd:
                handled = self.registry.handle(cmd, payload)
                if handled is not None:
                    print(handled)
                    continue
                print(f"Command '/{cmd}' tidak dikenali.")
                continue

            natural_action = self._try_natural_tool_action(user_input)
            if natural_action is not None:
                print(natural_action)
                # simpan agar tetap masuk memori sesi
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": natural_action})
                continue

            ai_plan = self.ai_client.plan_workspace_action(
                user_input=user_input,
                model_type=self.active_model,
                behavior_rules=self.behavior_rules,
            )
            planned_action = self._execute_planned_workspace_action(ai_plan) if ai_plan else None
            if planned_action is not None:
                print(planned_action)
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": planned_action})
                continue

            print("AI sedang berpikir...")
            history_for_model = self.history[-self.config.max_history_messages :]
            answer = self.ai_client.execute_task(
                user_input,
                model_type=self.active_model,
                history=history_for_model,
                behavior_rules=self.behavior_rules,
            )
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": answer})
            print(f"KANA CORE: {answer}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    config = AgentConfig.from_env()
    app = KanaOmniAgent(config)
    app.run()


if __name__ == "__main__":
    main()
