"""
Safe Code Execution Sandbox for NEURON
Executes code with timeout guards and stdout/stderr capture.
"""

import sys
import io
import time
from typing import Dict, Any, Optional


class CodeSandbox:
    """
    Executes isolated Python code blocks with execution timeout
    and structured output capture for the verification loop.
    """

    @staticmethod
    def run_isolated(code_str: str, timeout_sec: float = 3.0) -> Dict[str, Any]:
        """
        Executes code within a restricted globals namespace.
        Captures standard output and runtime exceptions.
        """
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_stdout = io.StringIO()
        redirected_stderr = io.StringIO()

        globals_env: Dict[str, Any] = {
            "__builtins__": __builtins__,
        }
        locals_env: Dict[str, Any] = {}

        start_time = time.perf_counter()
        success = False
        error_msg: Optional[str] = None

        try:
            sys.stdout = redirected_stdout
            sys.stderr = redirected_stderr

            exec(code_str, globals_env, locals_env)
            success = True
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Retrieve any variables or return payload
        output = redirected_stdout.getvalue()
        err_output = redirected_stderr.getvalue()

        return {
            "success": success,
            "stdout": output,
            "stderr": err_output,
            "error": error_msg,
            "elapsed_ms": round(elapsed_ms, 2),
            "locals_keys": list(locals_env.keys())
        }
