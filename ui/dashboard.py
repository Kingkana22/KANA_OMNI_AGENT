from __future__ import annotations

import os
import threading
import customtkinter as ctk

from core.agentic_framework import AgenticFramework, FrameworkConfig


class KanaDashboard(ctk.CTk):
    def __init__(self, app: AgenticFramework, config: FrameworkConfig) -> None:
        super().__init__()
        self.app = app
        self.config = config

        self.title("KANA OMNI AGENT • Dashboard")
        self.geometry("1100x760")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
        self._build_console()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header,
            text="KANA Agentic Control Panel",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, padx=16, pady=14, sticky="w")

        meta = ctk.CTkLabel(
            header,
            text=f"Root: {self.config.cwd}   |   Model: {self.config.planner_model}",
            font=ctk.CTkFont(size=12),
        )
        meta.grid(row=0, column=1, padx=16, pady=14, sticky="e")

    def _build_controls(self) -> None:
        panel = ctk.CTkFrame(self)
        panel.grid(row=1, column=0, sticky="ew", padx=16, pady=10)
        panel.grid_columnconfigure(0, weight=1)

        self.task_input = ctk.CTkTextbox(panel, height=110)
        self.task_input.grid(row=0, column=0, columnspan=4, padx=14, pady=(14, 8), sticky="ew")
        self.task_input.insert("1.0", "Tulis task Anda di sini...")

        self.unsafe_var = ctk.BooleanVar(value=self.config.allow_unsafe)
        self.filter_var = ctk.BooleanVar(value=self.config.security_filter)

        unsafe_cb = ctk.CTkCheckBox(panel, text="Unsafe Mode", variable=self.unsafe_var, command=self._apply_policy)
        filter_cb = ctk.CTkCheckBox(panel, text="Security Filter", variable=self.filter_var, command=self._apply_policy)
        unsafe_cb.grid(row=1, column=0, padx=(14, 8), pady=(0, 12), sticky="w")
        filter_cb.grid(row=1, column=1, padx=8, pady=(0, 12), sticky="w")

        run_btn = ctk.CTkButton(panel, text="Execute Task", command=self._run_task)
        clear_btn = ctk.CTkButton(panel, text="Clear Output", command=self._clear_output)
        run_btn.grid(row=1, column=2, padx=8, pady=(0, 12), sticky="e")
        clear_btn.grid(row=1, column=3, padx=(8, 14), pady=(0, 12), sticky="e")

    def _build_console(self) -> None:
        console_wrap = ctk.CTkFrame(self)
        console_wrap.grid(row=2, column=0, sticky="nsew", padx=16, pady=(4, 16))
        console_wrap.grid_columnconfigure(0, weight=1)
        console_wrap.grid_rowconfigure(0, weight=1)

        self.output = ctk.CTkTextbox(console_wrap)
        self.output.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        self.output.insert("1.0", "[KANA] Dashboard siap.\n")

    def _apply_policy(self) -> None:
        allow_unsafe = bool(self.unsafe_var.get())
        security_filter = bool(self.filter_var.get())

        os.environ["AGENTIC_ALLOW_UNSAFE"] = "1" if allow_unsafe else "0"
        os.environ["AGENTIC_SECURITY_FILTER"] = "1" if security_filter else "0"
        self.app.apply_runtime_policy(allow_unsafe, security_filter)

        self._append_output(
            f"[POLICY] unsafe_mode={allow_unsafe} | security_filter={security_filter}\n"
        )

    def _run_task(self) -> None:
        task = self.task_input.get("1.0", "end").strip()
        if not task:
            return

        self._append_output(f"\n[TASK] {task}\n")

        def worker() -> None:
            result = self.app.handle(task)
            self.after(0, lambda: self._append_output(f"[RESULT]\n{result}\n"))

        threading.Thread(target=worker, daemon=True).start()

    def _clear_output(self) -> None:
        self.output.delete("1.0", "end")

    def _append_output(self, text: str) -> None:
        self.output.insert("end", text)
        self.output.see("end")


def run_dashboard() -> None:
    config = FrameworkConfig.from_env()
    app = AgenticFramework(config)
    ui = KanaDashboard(app=app, config=config)
    ui.mainloop()
