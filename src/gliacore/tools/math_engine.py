"""
Deterministic Mathematical Intelligence Engine for NEURON
Powered by SymPy for symbolic algebra, arithmetic, and verification.
"""

import sympy as sp
from typing import Dict, Any


class MathEngine:
    """
    Executes symbolic mathematics, algebraic simplification, equation solving,
    and exact arithmetic verification without neural hallucination.
    """

    @staticmethod
    def evaluate_expression(expr_str: str) -> Dict[str, Any]:
        """
        Safely evaluates an algebraic or arithmetic expression using SymPy.
        Example: '25 * 14 + 180 / 4' -> 395.0
        """
        try:
            # Parse using SymPy's safe sympify
            expr = sp.sympify(expr_str, evaluate=True)
            numerical_val = float(expr.evalf()) if expr.is_real else None
            return {
                "success": True,
                "exact": str(expr),
                "numeric": numerical_val,
                "is_integer": expr.is_integer,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "exact": None,
                "numeric": None,
                "is_integer": False,
                "error": f"Evaluation error: {str(e)}"
            }

    @staticmethod
    def solve_equation(equation_str: str, var_str: str = "x") -> Dict[str, Any]:
        """
        Solves an equation for a variable.
        Example: '2*x + 10 - 24' (meaning 2x + 10 = 24) or 'Eq(2*x + 10, 24)'
        """
        try:
            var = sp.Symbol(var_str)
            if "=" in equation_str and not equation_str.startswith("Eq"):
                left, right = equation_str.split("=", 1)
                eq = sp.Eq(sp.sympify(left), sp.sympify(right))
            else:
                eq = sp.sympify(equation_str)

            solutions = sp.solve(eq, var)
            return {
                "success": True,
                "variable": var_str,
                "solutions": [str(s) for s in solutions],
                "numeric_solutions": [float(s.evalf()) for s in solutions if s.is_real],
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "variable": var_str,
                "solutions": [],
                "numeric_solutions": [],
                "error": f"Solver error: {str(e)}"
            }

    @staticmethod
    def verify_equality(expr1_str: str, expr2_str: str) -> Dict[str, Any]:
        """
        Verifies if two expressions are mathematically identical.
        Prevents math hallucination in reasoning verification loops.
        """
        try:
            e1 = sp.sympify(expr1_str)
            e2 = sp.sympify(expr2_str)
            difference = sp.simplify(e1 - e2)
            is_equal = (difference == 0)
            return {
                "success": True,
                "is_equal": bool(is_equal),
                "difference": str(difference),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "is_equal": False,
                "difference": None,
                "error": f"Verification error: {str(e)}"
            }
