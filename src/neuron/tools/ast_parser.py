"""
Deterministic AST Code Intelligence Engine for NEURON
Statically validates code structure, syntax, and safety before execution.
"""

import ast
from typing import Dict, List, Any


class ASTParserTool:
    """
    Parses, validates, and analyzes Python source code without execution.
    Acts as the deterministic backbone for the Coder Neuron.
    """

    @staticmethod
    def validate_syntax(code_str: str) -> Dict[str, Any]:
        """
        Validates whether code string is syntactically valid Python.
        Returns line, column, and exact error message if invalid.
        """
        try:
            tree = ast.parse(code_str)
            return {
                "valid": True,
                "error": None,
                "line": None,
                "column": None,
                "node_count": len(list(ast.walk(tree)))
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "error": e.msg,
                "line": e.lineno,
                "column": e.offset,
                "node_count": 0
            }

    @staticmethod
    def extract_structure(code_str: str) -> Dict[str, Any]:
        """
        Extracts top-level functions, classes, imports, and docstrings.
        """
        try:
            tree = ast.parse(code_str)
            functions: List[str] = []
            classes: List[str] = []
            imports: List[str] = []

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    for alias in node.names:
                        imports.append(f"{mod}.{alias.name}")

            return {
                "success": True,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "error": None
            }
        except SyntaxError as e:
            return {
                "success": False,
                "functions": [],
                "classes": [],
                "imports": [],
                "error": f"SyntaxError: {e.msg} at line {e.lineno}"
            }
