"""
Repository Explorer & Codebase Inspection Tool for PROJECT: NEURON
Enables autonomous codebase exploration, AST symbol mapping, and dependency tracking.
"""

import os
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional


class RepositoryExplorer:
    """
    Safely inspects local code repositories, maps symbol hierarchies,
    and extracts file structures without manual user navigation.
    """

    EXCLUDED_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".vscode"}

    @classmethod
    def scan_directory(cls, root_path: str, max_depth: int = 4) -> Dict[str, Any]:
        """
        Builds structured directory tree and collects repository metrics.
        """
        p = Path(root_path).resolve()
        if not p.exists() or not p.is_dir():
            return {"success": False, "error": f"Path '{root_path}' does not exist or is not a directory"}

        files_list = []
        py_files_count = 0
        total_lines = 0

        for dirpath, dirnames, filenames in os.walk(p):
            # Prune excluded directories in-place
            dirnames[:] = [d for d in dirnames if d not in cls.EXCLUDED_DIRS]
            rel_dir = Path(dirpath).relative_to(p)
            depth = len(rel_dir.parts)
            if depth > max_depth:
                continue

            for fname in filenames:
                file_full = Path(dirpath) / fname
                rel_path = file_full.relative_to(p)
                is_py = fname.endswith(".py")
                if is_py:
                    py_files_count += 1
                    try:
                        with open(file_full, "r", encoding="utf-8", errors="ignore") as f:
                            lines = len(f.readlines())
                            total_lines += lines
                    except Exception:
                        lines = 0
                else:
                    lines = 0

                files_list.append({
                    "path": str(rel_path).replace("\\", "/"),
                    "is_python": is_py,
                    "size_bytes": file_full.stat().st_size,
                    "lines": lines
                })

        return {
            "success": True,
            "root": str(p),
            "total_files": len(files_list),
            "python_files": py_files_count,
            "total_python_lines": total_lines,
            "files": files_list[:100]  # bounded preview
        }

    @classmethod
    def extract_symbols(cls, file_path: str) -> Dict[str, Any]:
        """
        Parses a Python file and returns its classes, functions, and imported modules.
        """
        p = Path(file_path).resolve()
        if not p.exists() or not p.is_file():
            return {"success": False, "error": f"File '{file_path}' does not exist"}

        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            return {"success": False, "error": f"Parse error: {str(e)}"}

        classes = []
        functions = []
        imports = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in ast.iter_child_nodes(node) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes.append({"name": node.name, "line": node.lineno, "methods": methods})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({"name": node.name, "line": node.lineno})
            elif isinstance(node, ast.Import):
                for a in node.names:
                    imports.append(a.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for a in node.names:
                    imports.append(f"{mod}.{a.name}")

        return {
            "success": True,
            "file": str(p),
            "classes": classes,
            "functions": functions,
            "imports": imports
        }
