"""Agentic framework for local context-aware execution.

Fitur utama:
- Context awareness (tree direktori + ringkasan file + env terfilter).
- Planner berbasis LLM untuk menentukan aksi otomatis.
- Eksekusi tools lokal: terminal, baca/tulis file, list direktori.
- Guardrails opsional untuk command berisiko.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


@dataclass(frozen=True)
class FrameworkConfig:
    proxy_url: str
    proxy_key: str
    planner_model: str
    cwd: Path
    max_files: int = 250
    max_file_bytes: int = 6000
    max_actions: int = 5
    allow_unsafe: bool = False
    security_filter: bool = True

    @staticmethod
    def from_env() -> "FrameworkConfig":
        load_dotenv()
        proxy_url = os.getenv("PROXY_URL", "").strip()
        proxy_key = os.getenv("PROXY_KEY", "").strip()
        planner_model = os.getenv("MODEL_CODEX", "").strip() or os.getenv("MODEL_GEMINI", "").strip()

        missing = [
            key
            for key, value in {
                "PROXY_URL": proxy_url,
                "PROXY_KEY": proxy_key,
                "MODEL_CODEX/MODEL_GEMINI": planner_model,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Env belum lengkap: {', '.join(missing)}")

        return FrameworkConfig(
            proxy_url=proxy_url,
            proxy_key=proxy_key,
            planner_model=planner_model,
            cwd=Path.cwd(),
            allow_unsafe=os.getenv("AGENTIC_ALLOW_UNSAFE", "0").strip() == "1",
            security_filter=os.getenv("AGENTIC_SECURITY_FILTER", "1").strip() == "1",
        )


class ContextCollector:
    def __init__(self, root: Path, max_files: int, max_file_bytes: int) -> None:
        self.root = root
        self.max_files = max_files
        self.max_file_bytes = max_file_bytes

    def collect(self) -> Dict[str, Any]:
        files = self._collect_files()
        env_summary = self._collect_env()
        return {
            "cwd": str(self.root),
            "env": env_summary,
            "files": files,
        }

    def _collect_files(self) -> List[Dict[str, Any]]:
        collected: List[Dict[str, Any]] = []
        for path in sorted(self.root.rglob("*")):
            if len(collected) >= self.max_files:
                break
            if not path.is_file():
                continue
            if ".git" in path.parts:
                continue

            rel = str(path.relative_to(self.root))
            item: Dict[str, Any] = {"path": rel, "size": path.stat().st_size}

            if path.suffix.lower() in {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".sh"}:
                try:
                    item["snippet"] = path.read_text(encoding="utf-8", errors="ignore")[: self.max_file_bytes]
                except Exception as exc:
                    item["snippet_error"] = str(exc)
            collected.append(item)
        return collected

    @staticmethod
    def _collect_env() -> Dict[str, str]:
        allowed_prefixes = (
            "MODEL_",
            "PROXY_",
            "OPENAI_",
            "PYTHON",
            "VIRTUAL_ENV",
            "PATH",
        )
        summary: Dict[str, str] = {}
        for key, value in os.environ.items():
            if key.startswith(allowed_prefixes):
                summary[key] = value[:300]
        return summary


class LocalTools:
    def __init__(self, root: Path, allow_unsafe: bool = False, security_filter: bool = True) -> None:
        self.root = root.resolve()
        self.allow_unsafe = allow_unsafe
        self.security_filter = security_filter

    def run_terminal(self, command: str, timeout: int = 30) -> str:
        if self.security_filter and not self.allow_unsafe and self._looks_unsafe(command):
            return f"BLOCKED: Command berisiko ditolak (set AGENTIC_ALLOW_UNSAFE=1 untuk override): {command}"

        proc = subprocess.run(
            command,
            shell=True,
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=max(1, timeout),
        )
        stdout = (proc.stdout or "").strip()
        stderr = (proc.stderr or "").strip()
        return (
            f"exit_code={proc.returncode}\n"
            f"stdout:\n{stdout if stdout else '(kosong)'}\n"
            f"stderr:\n{stderr if stderr else '(kosong)'}"
        )

    def read_file(self, rel_path: str) -> str:
        target = self._safe_path(rel_path)
        if not target.exists() or not target.is_file():
            return f"ERROR: File tidak ditemukan: {rel_path}"
        return target.read_text(encoding="utf-8", errors="ignore")

    def write_file(self, rel_path: str, content: str) -> str:
        target = self._safe_path(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"OK: file tersimpan -> {rel_path}"

    def list_dir(self, rel_path: str = ".") -> str:
        target = self._safe_path(rel_path)
        if not target.exists() or not target.is_dir():
            return f"ERROR: Folder tidak ditemukan: {rel_path}"
        entries = sorted(target.iterdir())
        lines = []
        for entry in entries:
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"- {entry.name}{suffix}")
        return "\n".join(lines) if lines else "(folder kosong)"

    def _safe_path(self, rel_path: str) -> Path:
        rel = rel_path.strip() or "."
        candidate = (self.root / rel).resolve()
        if self.root not in candidate.parents and candidate != self.root:
            raise ValueError(f"Path di luar root project: {rel_path}")
        return candidate

    @staticmethod
    def _looks_unsafe(command: str) -> bool:
        lower = command.lower()
        blocked_tokens = [
            "rm -rf /",
            "mkfs",
            "shutdown",
            "reboot",
            "del /f /s /q",
            "format c:",
        ]
        return any(token in lower for token in blocked_tokens)


class AgenticFramework:
    def __init__(self, config: FrameworkConfig) -> None:
        self.config = config
        self.client = OpenAI(base_url=config.proxy_url, api_key=config.proxy_key)
        self.context = ContextCollector(config.cwd, config.max_files, config.max_file_bytes)
        self.tools = LocalTools(
            config.cwd,
            allow_unsafe=config.allow_unsafe,
            security_filter=config.security_filter,
        )

    def apply_runtime_policy(self, unsafe_mode: bool, security_filter: bool) -> None:
        self.tools.allow_unsafe = unsafe_mode
        self.tools.security_filter = security_filter

    def refresh_runtime_policy_from_env(self) -> None:
        self.apply_runtime_policy(
            unsafe_mode=os.getenv("AGENTIC_ALLOW_UNSAFE", "0").strip() == "1",
            security_filter=os.getenv("AGENTIC_SECURITY_FILTER", "1").strip() == "1",
        )

    def handle(self, user_task: str) -> str:
        self.refresh_runtime_policy_from_env()
        context_payload = self.context.collect()
        planner_output = self._plan_actions(user_task=user_task, context=context_payload)

        actions = planner_output.get("actions", [])
        if not isinstance(actions, list):
            actions = []

        results: List[Dict[str, str]] = []
        for action in actions[: self.config.max_actions]:
            result = self._execute_action(action)
            results.append({"action": json.dumps(action, ensure_ascii=False), "result": result})

        return self._finalize_response(user_task=user_task, plan=planner_output, results=results)

    def _plan_actions(self, user_task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "Kamu adalah agent planner. Balas JSON valid tanpa markdown. "
            "Format wajib: {\"actions\": [...], \"notes\": \"...\"}. "
            "Tools tersedia: run_terminal(command, timeout), read_file(path), write_file(path, content), list_dir(path). "
            "Gunakan tindakan minimal yang diperlukan untuk menyelesaikan task user."
        )

        response = self.client.chat.completions.create(
            model=self.config.planner_model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": user_task,
                            "context": context,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or "{}"
        return self._extract_json(raw)

    @staticmethod
    def _extract_json(raw: str) -> Dict[str, Any]:
        raw = raw.strip()
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            match_start = raw.find("{")
            match_end = raw.rfind("}")
            if match_start == -1 or match_end == -1 or match_end <= match_start:
                return {}
            try:
                parsed = json.loads(raw[match_start : match_end + 1])
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}

    def _execute_action(self, action: Dict[str, Any]) -> str:
        action_type = str(action.get("type", "")).strip()
        if action_type == "run_terminal":
            return self.tools.run_terminal(
                command=str(action.get("command", "")).strip(),
                timeout=int(action.get("timeout", 30)),
            )
        if action_type == "read_file":
            return self.tools.read_file(str(action.get("path", "")).strip())
        if action_type == "write_file":
            return self.tools.write_file(
                rel_path=str(action.get("path", "")).strip(),
                content=str(action.get("content", "")),
            )
        if action_type == "list_dir":
            return self.tools.list_dir(str(action.get("path", ".")).strip())
        return f"SKIP: action tidak dikenal -> {action_type}"

    def _finalize_response(self, user_task: str, plan: Dict[str, Any], results: List[Dict[str, str]]) -> str:
        payload = {
            "task": user_task,
            "plan": plan,
            "results": results,
        }
        response = self.client.chat.completions.create(
            model=self.config.planner_model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah assistant eksekusi agentic. Ringkas hasil tool run secara jelas, "
                        "jelaskan apa yang sudah dilakukan, dan langkah berikutnya jika ada."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        )
        return response.choices[0].message.content or "(tanpa respons)"


def run_repl() -> None:
    config = FrameworkConfig.from_env()
    app = AgenticFramework(config)

    print("=" * 62)
    print(" KANA Agentic Framework • Context-Aware Main Entry ".center(62, "="))
    print("=" * 62)
    print(f"Root project : {config.cwd}")
    print(f"Model planner: {config.planner_model}")
    print(f"Unsafe mode  : {'ON' if config.allow_unsafe else 'OFF'}")
    print(f"Filter mode  : {'ON' if config.security_filter else 'OFF'}")
    print("Ketik task natural. Contoh: 'analisa project ini dan jalankan test'.")
    print("Ketik 'exit' untuk keluar.")

    while True:
        user_input = input("\nTask> ").strip()
        if user_input.lower() == "exit":
            print("Selesai.")
            break
        if not user_input:
            continue

        try:
            result = app.handle(user_input)
            print(f"\nKANA AGENT:\n{result}")
        except Exception as exc:
            print(f"ERROR: {exc}")
