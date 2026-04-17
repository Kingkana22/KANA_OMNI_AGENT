import os
import sys
import importlib.util
from pathlib import Path


class RepoToolLoader:
    """Auto-discover and load tools from cloned repositories"""

    def __init__(self):
        self.repo_root = Path(__file__).resolve().parent
        self.reference_codes_dir = self.repo_root / "knowledge_base" / "reference_codes"
        self.discovered_tools = {}
        self.loaded_modules = {}
        self.discover_tools()

    def discover_tools(self):
        """Auto-discover executable Python tools in cloned repos"""
        if not self.reference_codes_dir.exists():
            print(f"[!] Reference codes directory not found: {self.reference_codes_dir}")
            return

        print(f"[*] Scanning {self.reference_codes_dir} for tools...\n")

        for repo_path in self.reference_codes_dir.iterdir():
            if not repo_path.is_dir():
                continue

            self._scan_directory(repo_path)

    def _scan_directory(self, directory, depth=0, max_depth=3):
        """Recursively scan directory for Python tools"""
        if depth > max_depth:
            return

        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix == ".py":
                    self._analyze_python_file(item)
                elif item.is_dir() and not item.name.startswith(('.', '__')):
                    self._scan_directory(item, depth + 1, max_depth)
        except (PermissionError, OSError):
            pass

    def _analyze_python_file(self, file_path):
        """Analyze Python file for executable tools"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for main execution patterns
            has_main = 'if __name__ == "__main__"' in content
            has_class = 'class ' in content
            has_click = '@click.' in content or 'import click' in content
            has_argparse = 'argparse' in content

            if has_main or has_click or has_argparse:
                rel_path = str(file_path.relative_to(self.repo_root))
                repo_name = file_path.relative_to(self.reference_codes_dir).parts[0]

                self.discovered_tools[rel_path] = {
                    "path": file_path,
                    "repo": repo_name,
                    "type": "executable",
                    "has_main": has_main,
                    "has_cli": has_click or has_argparse,
                    "has_classes": has_class
                }

                print(f"[+] Found tool: {file_path.name} (from {repo_name})")
        except Exception as e:
            pass

    def load_tool_module(self, file_path):
        """Dynamically load a Python module as a tool"""
        try:
            spec = importlib.util.spec_from_file_location(
                file_path.stem,
                file_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[file_path.stem] = module
            spec.loader.exec_module(module)

            self.loaded_modules[str(file_path)] = module
            return module, None
        except Exception as e:
            return None, f"Error loading {file_path.name}: {e}"

    def list_discovered_tools(self):
        """List all discovered tools"""
        if not self.discovered_tools:
            print("[!] No tools discovered")
            return

        print(f"\n=== DISCOVERED TOOLS ({len(self.discovered_tools)}) ===\n")
        
        current_repo = None
        for tool_path, info in self.discovered_tools.items():
            if info["repo"] != current_repo:
                current_repo = info["repo"]
                print(f"\n📦 {current_repo}:")

            flags = []
            if info["has_main"]:
                flags.append("Main")
            if info["has_cli"]:
                flags.append("CLI")
            if info["has_classes"]:
                flags.append("Classes")

            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"   • {info['path'].name}{flag_str}")

    def run_tool_interactive(self):
        """Interactive tool selection and execution"""
        if not self.discovered_tools:
            print("[!] No tools discovered. Try injecting repositories first.")
            return

        print(f"\n=== RUN CLONED REPO TOOLS ({len(self.discovered_tools)}) ===\n")

        tools_list = list(self.discovered_tools.items())

        for idx, (tool_path, info) in enumerate(tools_list, 1):
            print(f"[{idx}] {info['path'].name} ({info['repo']})")

        choice = input("\n[?] Select tool (or 0 to cancel): ").strip()

        try:
            idx = int(choice) - 1
            if idx < 0:
                return
            if idx >= len(tools_list):
                print("[!] Invalid choice")
                return

            tool_path, info = tools_list[idx]
            self._execute_tool(info['path'])
        except ValueError:
            print("[!] Invalid input")

    def _execute_tool(self, file_path):
        """Execute a tool"""
        print(f"\n[*] Loading {file_path.name}...\n")

        try:
            # Try to load and execute
            module, error = self.load_tool_module(file_path)

            if error:
                print(f"[!] {error}")
                return

            # Check if module has main function or if __name__ check would trigger
            if hasattr(module, 'main'):
                module.main()
            else:
                print(f"[+] Module loaded. Look for main() function or run directly.")
                print(f"[*] Module: {module}")

        except KeyboardInterrupt:
            print("\n[!] Tool interrupted")
        except Exception as e:
            print(f"[!] Error executing tool: {e}")
            import traceback
            traceback.print_exc()

    def get_tool_by_repo(self, repo_name):
        """Get all tools from a specific repo"""
        tools = [
            (path, info) for path, info in self.discovered_tools.items()
            if info["repo"] == repo_name
        ]
        return tools

    def auto_load_all_executables(self):
        """Auto-load all discovered executable tools"""
        print(f"\n[*] Auto-loading {len(self.discovered_tools)} tools...\n")

        for tool_path, info in self.discovered_tools.items():
            module, error = self.load_tool_module(info['path'])
            if error:
                print(f"[-] {error}")
            else:
                print(f"[+] Loaded: {info['path'].name}")

        print(f"\n[+] All tools loaded: {len(self.loaded_modules)} modules")


if __name__ == "__main__":
    loader = RepoToolLoader()
    loader.list_discovered_tools()
    loader.run_tool_interactive()
