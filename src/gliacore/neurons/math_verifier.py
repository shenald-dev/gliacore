"""
Mathematical Intelligence & Verification Neuron for NEURON
Deterministic numerical and symbolic processing via SymPy.
"""

from typing import Dict, Any
import re
from gliacore.neurons.base import BaseNeuron
from gliacore.tools.math_engine import MathEngine
from gliacore.synapse.bus import SynapseBus


class MathVerifierNeuron(BaseNeuron):
    """
    Solves mathematical equations, evaluates arithmetic expressions,
    and deterministically verifies claims made by other neurons.
    """

    def __init__(self, bus: SynapseBus = None):
        super().__init__(
            neuron_id="neuron_math_01",
            name="Mathematical Intelligence & Verifier Neuron",
            specialization="math",
            bus=bus
        )
        self.engine = MathEngine()

    def execute(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task_payload.get("prompt", "")
        expression = task_payload.get("expression")
        equation = task_payload.get("equation")

        # 1. Direct expression evaluation if provided
        if expression:
            eval_res = self.engine.evaluate_expression(expression)
            return {
                "operation": "evaluate",
                "expression": expression,
                "result": eval_res
            }

        # 2. Equation solver if provided
        if equation:
            var = task_payload.get("variable", "x")
            solve_res = self.engine.solve_equation(equation, var)
            return {
                "operation": "solve",
                "equation": equation,
                "variable": var,
                "result": solve_res
            }

        # 3. Automatic extraction from prompt
        # Detect simple expressions like "25 * 4 + 10" or "solve 2*x + 5 = 15"
        solve_match = re.search(r"solve\s+([0-9a-zA-Z\s\+\-\*\/\^\=]+)", prompt, re.IGNORECASE)
        if solve_match:
            eq_str = solve_match.group(1).strip()
            solve_res = self.engine.solve_equation(eq_str)
            return {
                "operation": "solve",
                "extracted_equation": eq_str,
                "result": solve_res
            }

        # Extract arithmetic expression like "(45 * 12) + (180 / 3)"
        math_expr_match = re.search(r"([\d\.\s\+\-\*\/\(\)\^]{3,})", prompt)
        if math_expr_match:
            cand = math_expr_match.group(1).strip()
            # Verify candidate contains at least one operator
            if any(op in cand for op in ["+", "-", "*", "/", "^"]):
                eval_res = self.engine.evaluate_expression(cand)
                if eval_res["success"]:
                    return {
                        "operation": "evaluate",
                        "extracted_expression": cand,
                        "result": eval_res
                    }

        # Symbolic derivation fallback
        return {
            "operation": "symbolic_analysis",
            "prompt": prompt,
            "status": "No direct arithmetic or polynomial detected for deterministic solving"
        }
