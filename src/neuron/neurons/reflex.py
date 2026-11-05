"""
Reflex & Guardrail Neuron for PROJECT: NEURON
Ultra-fast semantic intent classifier and risk assessor.
"""

from typing import Dict, Any, List
import re
from neuron.neurons.base import BaseNeuron
from neuron.synapse.bus import SynapseBus


class ReflexNeuron(BaseNeuron):
    """
    Sub-millisecond reflex unit.
    Extracts query intent, detects dangerous payloads, and decides routing targets.
    """

    def __init__(self, bus: SynapseBus = None):
        super().__init__(
            neuron_id="neuron_reflex_01",
            name="Reflex & Guardrail Neuron",
            specialization="reflex",
            bus=bus
        )

    def execute(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task_payload.get("prompt", "").strip()

        # 1. Security & Guardrail Check
        risk_patterns = [
            r"rm\s+-rf",
            r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # fork bomb
            r"DROP\s+DATABASE",
            r"__import__\s*\(\s*['\"]os['\"]\s*\)\.system",
        ]
        is_risky = any(re.search(pat, prompt, re.IGNORECASE) for pat in risk_patterns)
        if is_risky:
            return {
                "category": "BLOCKED",
                "risk_level": "HIGH",
                "target_neurons": [],
                "reason": "Security guardrail triggered by high-risk payload"
            }

        # 2. Heuristic Semantic Intent Categorization
        prompt_lower = prompt.lower()
        has_math = any(kw in prompt_lower for kw in [
            "calculate", "solve", "equation", "math", "derive", "integral", "sum of",
            "multiply", "divide", "+", "-", "*", "/", "=", "^", "sqrt"
        ]) and re.search(r"\d+", prompt)

        has_code = any(kw in prompt_lower for kw in [
            "def ", "function", "class ", "python", "code", "algorithm", "implement",
            "binary search", "regex", "script", "return ", "syntax"
        ])

        has_knowledge = any(kw in prompt_lower for kw in [
            "what is", "who is", "explain", "history", "documentation", "lookup", "retrieve"
        ])

        target_neurons: List[str] = []
        if has_math and has_code:
            category = "COMPOSITE"
            target_neurons = ["neuron_planner_01", "neuron_math_01", "neuron_coder_01"]
        elif has_math:
            category = "MATH"
            target_neurons = ["neuron_math_01"]
        elif has_code:
            category = "CODE"
            target_neurons = ["neuron_coder_01"]
        elif has_knowledge:
            category = "KNOWLEDGE"
            target_neurons = ["neuron_planner_01"]
        else:
            category = "REASONING"
            target_neurons = ["neuron_planner_01"]

        return {
            "category": category,
            "risk_level": "LOW",
            "target_neurons": target_neurons,
            "estimated_complexity": "HIGH" if category == "COMPOSITE" else "NORMAL"
        }
