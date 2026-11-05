"""
Planning & Reasoning Neuron for PROJECT: NEURON
Decomposes complex problems into dependency DAGs and execution steps.
"""

from typing import Dict, Any, List
from neuron.neurons.base import BaseNeuron
from neuron.synapse.bus import SynapseBus


class PlannerNeuron(BaseNeuron):
    """
    Cognitive planning unit.
    Transforms arbitrary user goals into structured sub-tasks with verification checkpoints.
    """

    def __init__(self, bus: SynapseBus = None):
        super().__init__(
            neuron_id="neuron_planner_01",
            name="Cognitive Planner & Reasoning Neuron",
            specialization="planner",
            bus=bus
        )

    def execute(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task_payload.get("prompt", "")
        category = task_payload.get("category", "GENERAL")

        # Decompose task into sequential stages
        stages: List[Dict[str, Any]] = []

        if category == "MATH" or "solve" in prompt.lower() or "calculate" in prompt.lower():
            stages = [
                {
                    "step": 1,
                    "target_neuron": "neuron_math_01",
                    "action": "extract_and_evaluate",
                    "description": "Parse equation or arithmetic expression via SymPy"
                },
                {
                    "step": 2,
                    "target_neuron": "neuron_verifier_01",
                    "action": "verify_result",
                    "description": "Verify mathematical consistency against original constraints"
                }
            ]
        elif category == "CODE" or "implement" in prompt.lower() or "function" in prompt.lower():
            stages = [
                {
                    "step": 1,
                    "target_neuron": "neuron_coder_01",
                    "action": "synthesize_and_ast_check",
                    "description": "Synthesize Python solution and validate AST structure"
                },
                {
                    "step": 2,
                    "target_neuron": "neuron_coder_01",
                    "action": "sandbox_execution",
                    "description": "Execute code in sandbox to assert runtime invariants"
                }
            ]
        else:
            stages = [
                {
                    "step": 1,
                    "target_neuron": "neuron_reflex_01",
                    "action": "extract_invariants",
                    "description": "Extract domain entities and intent constraints"
                },
                {
                    "step": 2,
                    "target_neuron": "neuron_planner_01",
                    "action": "synthesize_reasoning",
                    "description": "Synthesize response using verified intermediate artifacts"
                }
            ]

        return {
            "prompt": prompt,
            "category": category,
            "stages": stages,
            "stage_count": len(stages),
            "verification_required": True
        }
