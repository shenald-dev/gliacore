"""
Unit tests for Deterministic Tools (MathEngine, ASTParserTool, CodeSandbox)
"""

import pytest
from gliacore.tools.math_engine import MathEngine
from gliacore.tools.ast_parser import ASTParserTool
from gliacore.tools.code_sandbox import CodeSandbox


def test_math_engine_evaluate():
    engine = MathEngine()
    res = engine.evaluate_expression("25 * 4 + 180 / 3")
    assert res["success"] is True
    assert res["numeric"] == 160.0


def test_math_engine_solve():
    engine = MathEngine()
    res = engine.solve_equation("3*x - 15 = 0", var_str="x")
    assert res["success"] is True
    assert res["solutions"] == ["5"]


def test_ast_parser_valid_code():
    code = """
def multiply(a: int, b: int) -> int:
    return a * b
"""
    res = ASTParserTool.validate_syntax(code)
    assert res["valid"] is True
    assert res["error"] is None

    struct = ASTParserTool.extract_structure(code)
    assert struct["success"] is True
    assert "multiply" in struct["functions"]


def test_ast_parser_syntax_error():
    broken_code = "def broken(a, b: return a +"
    res = ASTParserTool.validate_syntax(broken_code)
    assert res["valid"] is False
    assert res["error"] is not None
    assert res["line"] is not None


def test_code_sandbox_execution():
    code = """
def test_func():
    return 42

result = test_func()
print(f"Output: {result}")
"""
    res = CodeSandbox.run_isolated(code)
    assert res["success"] is True
    assert "Output: 42" in res["stdout"]
    assert "result" in res["locals_keys"]
