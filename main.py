import sys

from core.agentic_framework import run_repl
from ui.dashboard import run_dashboard


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_repl()
    else:
        run_dashboard()
