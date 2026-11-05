"""
Hardened Safe Code Execution Sandbox for NEURON
Enforces AST pre-screening, restricted builtins, and true OS-level timeout termination.
"""

import sys
import ast
import json
import time
import subprocess
from typing import Dict, Any, Set

FORBIDDEN_MODULES: Set[str] = {
    "os", "sys", "subprocess", "shutil", "socket", "ctypes", "pathlib", "pty",
    "posix", "nt", "importlib", "_thread", "threading", "multiprocessing"
}

FORBIDDEN_CALLS: Set[str] = {
    "open", "eval", "exec", "compile", "__import__", "getattr", "setattr",
    "delattr", "globals", "locals", "memoryview"
}

FORBIDDEN_ATTRS: Set[str] = {
    "__subclasses__", "__globals__", "__code__", "__closure__", "__dict__"
}


class CodeSandbox:
    """
    Production-grade sandbox for executing untrusted Python snippets.
    Combines static AST safety verification with subprocess isolation and hard timeouts.
    """

    @staticmethod
    def inspect_safety(code_str: str) -> Dict[str, Any]:
        """
        Statically inspects AST to prevent execution of unauthorized system calls,
        file access, network sockets, or dunder-attribute traversal.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return {"safe": False, "reason": f"SyntaxError: {e.msg} at line {e.lineno}"}

        for node in ast.walk(tree):
            # Check module imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod_root = alias.name.split(".")[0]
                    if mod_root in FORBIDDEN_MODULES:
                        return {"safe": False, "reason": f"Import of restricted module '{alias.name}' is prohibited"}
            elif isinstance(node, ast.ImportFrom):
                mod_root = (node.module or "").split(".")[0]
                if mod_root in FORBIDDEN_MODULES:
                    return {"safe": False, "reason": f"Import from restricted module '{node.module}' is prohibited"}

            # Check direct function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                    return {"safe": False, "reason": f"Call to dangerous builtin '{node.func.id}()' is prohibited"}

            # Check attribute access
            elif isinstance(node, ast.Attribute):
                if node.attr in FORBIDDEN_ATTRS:
                    return {"safe": False, "reason": f"Access to restricted attribute '{node.attr}' is prohibited"}

        return {"safe": True, "reason": None}

    @classmethod
    def run_isolated(cls, code_str: str, timeout_sec: float = 3.0) -> Dict[str, Any]:
        """
        Executes code within a hardened sandbox with OS-level timeout enforcement.
        1. Pre-screens AST for security risks.
        2. Executes in an isolated Python subprocess.
        3. Captures stdout/stderr safely without process-wide pollution.
        """
        start_time = time.perf_counter()

        # Step 1: Pre-screen AST
        safety = cls.inspect_safety(code_str)
        if not safety["safe"]:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "success": False,
                "stdout": "",
                "stderr": safety["reason"],
                "error": f"SecurityViolation: {safety['reason']}",
                "elapsed_ms": round(elapsed_ms, 2),
                "locals_keys": []
            }

        # Step 2: Prepare isolated wrapper code with restricted builtins
        wrapper_code = f"""
import sys
import json

_safe_builtins = {{
    'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool, 'chr': chr,
    'complex': complex, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
    'filter': filter, 'float': float, 'format': format, 'frozenset': frozenset,
    'hasattr': hasattr, 'hash': hash, 'hex': hex, 'int': int, 'isinstance': isinstance,
    'issubclass': issubclass, 'iter': iter, 'len': len, 'list': list, 'map': map,
    'max': max, 'min': min, 'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
    'print': print, 'range': range, 'repr': repr, 'reversed': reversed, 'round': round,
    'set': set, 'slice': slice, 'sorted': sorted, 'str': str, 'sum': sum,
    'tuple': tuple, 'type': type, 'zip': zip, 'Exception': Exception,
    'ValueError': ValueError, 'TypeError': TypeError, 'IndexError': IndexError,
    'KeyError': KeyError, 'ZeroDivisionError': ZeroDivisionError
}}

_env = {{'__builtins__': _safe_builtins}}
try:
    exec({repr(code_str)}, _env, _env)
    _user_keys = [k for k in _env.keys() if not k.startswith('_') and k not in _safe_builtins]
    sys.stdout.write("\\n__LOCALS_KEYS__:" + json.dumps(_user_keys) + "\\n")
except Exception as _e:
    sys.stderr.write(f"{{type(_e).__name__}}: {{str(_e)}}")
    sys.exit(1)
"""

        # Step 3: Run isolated subprocess with hard timeout
        try:
            proc = subprocess.run(
                [sys.executable, "-c", wrapper_code],
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            success = (proc.returncode == 0)

            stdout = proc.stdout
            locals_keys = []
            if "__LOCALS_KEYS__:" in stdout:
                parts = stdout.split("__LOCALS_KEYS__:")
                stdout = parts[0].rstrip("\r\n")
                if len(parts) > 1:
                    try:
                        raw_keys = parts[1].strip().splitlines()[0]
                        locals_keys = json.loads(raw_keys)
                    except Exception:
                        pass

            return {
                "success": success,
                "stdout": stdout,
                "stderr": proc.stderr,
                "error": proc.stderr.strip() if not success else None,
                "elapsed_ms": round(elapsed_ms, 2),
                "locals_keys": locals_keys
            }
        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_sec}s",
                "error": f"TimeoutError: Execution exceeded {timeout_sec} seconds limit",
                "elapsed_ms": round(elapsed_ms, 2),
                "locals_keys": []
            }
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "error": f"ExecutionError: {str(e)}",
                "elapsed_ms": round(elapsed_ms, 2),
                "locals_keys": []
            }
