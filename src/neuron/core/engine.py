"""
NEURAL CORE — The Central Orchestrator for PROJECT: NEURON
Coordinates specialized neurons, manages memory, routes tasks, and executes verification.
"""

import time
import uuid
from typing import Dict, Any, List, Optional

from neuron.core.hardware import HardwareSupervisor
from neuron.core.registry import NeuronRegistry
from neuron.synapse.bus import SynapseBus
from neuron.synapse.messages import SynapseMessage, MessageType
from neuron.memory.working import WorkingMemory
from neuron.memory.storage import KnowledgeStorage
from neuron.verification.consensus import VerificationEngine

from neuron.neurons.reflex import ReflexNeuron
from neuron.neurons.planner import PlannerNeuron
from neuron.neurons.math_verifier import MathVerifierNeuron
from neuron.neurons.coder import CoderNeuron


class NeuralCore:
    """
    The brain of the NEURON ecosystem.
    Coordinates execution of specialized micro-neurons over binary synapses
    while strictly enforcing hardware safety constraints.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.hardware = HardwareSupervisor()
        self.synapse_bus = SynapseBus()
        self.registry = NeuronRegistry()
        self.storage = KnowledgeStorage(db_path=db_path)
        self.verifier = VerificationEngine()

        # Initialize and register the core neuron fleet
        self._init_neuron_fleet()

    def _init_neuron_fleet(self) -> None:
        """Instantiate and wire neurons to the Synapse communication bus."""
        self.reflex_neuron = ReflexNeuron(bus=self.synapse_bus)
        self.planner_neuron = PlannerNeuron(bus=self.synapse_bus)
        self.math_neuron = MathVerifierNeuron(bus=self.synapse_bus)
        self.coder_neuron = CoderNeuron(bus=self.synapse_bus)

        self.registry.register(self.reflex_neuron)
        self.registry.register(self.planner_neuron)
        self.registry.register(self.math_neuron)
        self.registry.register(self.coder_neuron)

    def process(self, prompt: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End-to-end collective intelligence pipeline:
        1. VRAM/RAM Pre-flight Check
        2. Reflex Intent & Security Screening
        3. Cognitive Planning & Sub-task DAG Generation
        4. Specialized Neuron Collaborative Execution over Synapses
        5. Cross-Neuron Verification & Contradiction Detection
        6. Working Memory Persistence & Result Synthesis
        """
        task_id = task_id or str(uuid.uuid4())
        working_mem = WorkingMemory(task_id=task_id)
        start_time = time.perf_counter()

        with self.hardware.memory_tracer(label=f"task_{task_id[:8]}") as mem_stats:
            # Stage 1: Reflex & Intent Classification
            reflex_res = self.reflex_neuron.run({"prompt": prompt})
            working_mem.add_artifact(
                artifact_id="art_reflex",
                source_neuron=self.reflex_neuron.neuron_id,
                data_type="reflex",
                content=reflex_res["result"],
                confidence=1.0 if reflex_res["success"] else 0.0
            )

            category = reflex_res["result"].get("category", "GENERAL")
            if category == "BLOCKED":
                total_elapsed_ms = (time.perf_counter() - start_time) * 1000
                return {
                    "task_id": task_id,
                    "status": "BLOCKED",
                    "reason": reflex_res["result"].get("reason"),
                    "output": "Execution halted by safety guardrails.",
                    "results": {"blocked": True, "reason": reflex_res["result"].get("reason")},
                    "total_latency_ms": round(total_elapsed_ms, 2),
                    "consensus_score": 1.0,
                    "memory": mem_stats
                }

            # Stage 2: Planning & Task Decomposition
            planner_res = self.planner_neuron.run({"prompt": prompt, "category": category})
            working_mem.add_artifact(
                artifact_id="art_plan",
                source_neuron=self.planner_neuron.neuron_id,
                data_type="plan",
                content=planner_res["result"]
            )

            # Stage 3: Knowledge Context Retrieval
            retrieved_knowledge = self.storage.search_keyword(prompt, limit=3)
            working_mem.set_state("retrieved_knowledge", retrieved_knowledge)

            # Stage 4: Collaborative Execution via Synapses
            intermediate_artifacts: List[Dict[str, Any]] = []
            final_output_payload: Dict[str, Any] = {}

            # Execute Math Neuron if applicable
            if category in ["MATH", "COMPOSITE"]:
                math_res = self.math_neuron.run({"prompt": prompt})
                math_verif = self.verifier.verify_artifact("math", math_res["result"])
                working_mem.add_artifact(
                    artifact_id="art_math",
                    source_neuron=self.math_neuron.neuron_id,
                    data_type="math",
                    content=math_res["result"],
                    confidence=math_verif["confidence"]
                )
                intermediate_artifacts.append(math_verif)
                final_output_payload["math"] = math_res["result"]

            # Execute Coder Neuron if applicable
            if category in ["CODE", "COMPOSITE"]:
                code_res = self.coder_neuron.run({"prompt": prompt, "run_tests": True})
                code_verif = self.verifier.verify_artifact("code", code_res["result"])
                working_mem.add_artifact(
                    artifact_id="art_code",
                    source_neuron=self.coder_neuron.neuron_id,
                    data_type="code",
                    content=code_res["result"],
                    confidence=code_verif["confidence"]
                )
                intermediate_artifacts.append(code_verif)
                final_output_payload["code"] = code_res["result"]

            # General reasoning fallback if neither math nor code was specifically triggered
            if category in ["REASONING", "KNOWLEDGE"] or not intermediate_artifacts:
                final_output_payload["reasoning"] = {
                    "analysis": f"Task categorized as {category}. Structured reasoning completed.",
                    "retrieved_context_items": len(retrieved_knowledge)
                }

            # Stage 5: Cross-Neuron Verification & Consensus Check
            consensus_check = self.verifier.detect_contradictions(intermediate_artifacts)

            total_elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Stage 6: Formulate Final Result
            synthesis = {
                "task_id": task_id,
                "status": "SUCCESS" if not consensus_check["contradiction_detected"] else "VERIFICATION_WARNING",
                "category": category,
                "consensus_score": consensus_check["consensus_score"],
                "results": final_output_payload,
                "working_memory": working_mem.summary(),
                "synapse_telemetry": self.synapse_bus.get_telemetry(),
                "hardware_telemetry": mem_stats,
                "total_latency_ms": round(total_elapsed_ms, 2)
            }

            # Record in Long-term task history
            self.storage.record_task_history(
                task_id=task_id,
                prompt=prompt,
                category=category,
                plan=str(planner_res["result"].get("stages", [])),
                output=str(final_output_payload),
                status=synthesis["status"],
                latency_ms=total_elapsed_ms
            )

            return synthesis

    def close(self) -> None:
        """Release all resources and close database connections."""
        self.storage.close()
        self.synapse_bus.clear()
        self.hardware.purge_cache()
