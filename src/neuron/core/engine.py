"""
NEURAL CORE — The Central Orchestrator for PROJECT: NEURON
Coordinates specialized neurons, manages memory, routes tasks, and executes verification.
"""

import time
import uuid
import psutil
from typing import Dict, Any, List, Optional

from neuron.core.hardware import HardwareSupervisor
from neuron.core.registry import NeuronRegistry
from neuron.core.model_runner import ModelRunner
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
        self.model_runner = ModelRunner(hardware_supervisor=self.hardware)

        # Operational metrics
        self.total_completed_tasks: int = 0
        self.total_failed_tasks: int = 0
        self.total_blocked_tasks: int = 0
        self.task_latencies: List[float] = []

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

    def process(self, prompt: str, task_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
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
        execution_timeline: List[Dict[str, Any]] = []

        with self.hardware.memory_tracer(label=f"task_{task_id[:8]}") as mem_stats:
            # Stage 1: Reflex & Intent Classification
            t0 = time.perf_counter()
            reflex_res = self.reflex_neuron.run({"prompt": prompt})
            t_reflex = round((time.perf_counter() - t0) * 1000, 2)

            category = reflex_res["result"].get("category", "GENERAL")
            is_blocked = (category == "BLOCKED")

            execution_timeline.append({
                "stage": "Reflex Screening & Security",
                "neuron": self.reflex_neuron.neuron_id,
                "state": "blocked" if is_blocked else "completed",
                "duration_ms": t_reflex,
                "output": reflex_res["result"]
            })

            working_mem.add_artifact(
                artifact_id="art_reflex",
                source_neuron=self.reflex_neuron.neuron_id,
                data_type="reflex",
                content=reflex_res["result"],
                confidence=1.0 if reflex_res["success"] else 0.0
            )

            if is_blocked:
                self.total_blocked_tasks += 1
                total_elapsed_ms = (time.perf_counter() - start_time) * 1000
                self.task_latencies.append(total_elapsed_ms)
                return {
                    "task_id": task_id,
                    "session_id": session_id,
                    "status": "BLOCKED",
                    "reason": reflex_res["result"].get("reason"),
                    "output": "Execution halted by safety guardrails.",
                    "results": {"blocked": True, "reason": reflex_res["result"].get("reason")},
                    "execution_timeline": execution_timeline,
                    "total_latency_ms": round(total_elapsed_ms, 2),
                    "consensus_score": 1.0,
                    "memory": mem_stats
                }

            # Stage 2: Planning & Task Decomposition
            t0 = time.perf_counter()
            planner_res = self.planner_neuron.run({"prompt": prompt, "category": category})
            t_plan = round((time.perf_counter() - t0) * 1000, 2)

            execution_timeline.append({
                "stage": "Cognitive Planning",
                "neuron": self.planner_neuron.neuron_id,
                "state": "completed",
                "duration_ms": t_plan,
                "output": planner_res["result"]
            })

            working_mem.add_artifact(
                artifact_id="art_plan",
                source_neuron=self.planner_neuron.neuron_id,
                data_type="plan",
                content=planner_res["result"]
            )

            # Stage 3: Knowledge Context Retrieval
            t0 = time.perf_counter()
            retrieved_knowledge = self.storage.search_keyword(prompt, limit=3)
            t_retrieval = round((time.perf_counter() - t0) * 1000, 2)
            working_mem.set_state("retrieved_knowledge", retrieved_knowledge)

            execution_timeline.append({
                "stage": "Knowledge Retrieval",
                "neuron": "storage_sqlite",
                "state": "completed",
                "duration_ms": t_retrieval,
                "output": {"retrieved_items": len(retrieved_knowledge)}
            })

            # Stage 4: Collaborative Execution via Synapses
            intermediate_artifacts: List[Dict[str, Any]] = []
            final_output_payload: Dict[str, Any] = {}

            # Execute Math Neuron if applicable
            if category in ["MATH", "COMPOSITE"]:
                t0 = time.perf_counter()
                math_res = self.math_neuron.run({"prompt": prompt})
                math_verif = self.verifier.verify_artifact("math", math_res["result"])
                t_math = round((time.perf_counter() - t0) * 1000, 2)

                working_mem.add_artifact(
                    artifact_id="art_math",
                    source_neuron=self.math_neuron.neuron_id,
                    data_type="math",
                    content=math_res["result"],
                    confidence=math_verif["confidence"]
                )
                intermediate_artifacts.append(math_verif)
                final_output_payload["math"] = math_res["result"]

                execution_timeline.append({
                    "stage": "Mathematical Reasoning (SymPy)",
                    "neuron": self.math_neuron.neuron_id,
                    "state": "completed" if math_verif["verified"] else "failed",
                    "duration_ms": t_math,
                    "output": math_res["result"]
                })

            # Execute Coder Neuron if applicable
            if category in ["CODE", "COMPOSITE"]:
                t0 = time.perf_counter()
                code_res = self.coder_neuron.run({"prompt": prompt, "run_tests": True})
                code_verif = self.verifier.verify_artifact("code", code_res["result"])
                t_code = round((time.perf_counter() - t0) * 1000, 2)

                working_mem.add_artifact(
                    artifact_id="art_code",
                    source_neuron=self.coder_neuron.neuron_id,
                    data_type="code",
                    content=code_res["result"],
                    confidence=code_verif["confidence"]
                )
                intermediate_artifacts.append(code_verif)
                final_output_payload["code"] = code_res["result"]

                execution_timeline.append({
                    "stage": "Code Synthesis & AST Validation",
                    "neuron": self.coder_neuron.neuron_id,
                    "state": "completed" if code_verif["verified"] else "failed",
                    "duration_ms": t_code,
                    "output": {"syntax_valid": code_res["result"].get("syntax_valid")}
                })

            # General reasoning / Model generation fallback
            if category in ["REASONING", "KNOWLEDGE", "PLANNING"] or not intermediate_artifacts:
                t0 = time.perf_counter()
                gen_res = self.model_runner.generate(prompt)
                t_gen = round((time.perf_counter() - t0) * 1000, 2)
                final_output_payload["reasoning"] = {
                    "text": gen_res["text"],
                    "mode": gen_res["mode"],
                    "tokens": gen_res["tokens_generated"]
                }
                execution_timeline.append({
                    "stage": "Foundation Model Inference",
                    "neuron": "model_runner",
                    "state": "completed",
                    "duration_ms": t_gen,
                    "output": {"mode": gen_res["mode"], "tokens": gen_res["tokens_generated"]}
                })

            # Stage 5: Cross-Neuron Verification & Consensus Check
            t0 = time.perf_counter()
            consensus_check = self.verifier.detect_contradictions(intermediate_artifacts)
            t_consensus = round((time.perf_counter() - t0) * 1000, 2)

            execution_timeline.append({
                "stage": "Consensus & Contradiction Verification",
                "neuron": "verification_engine",
                "state": "completed" if not consensus_check["contradiction_detected"] else "warning",
                "duration_ms": t_consensus,
                "output": consensus_check
            })

            total_elapsed_ms = (time.perf_counter() - start_time) * 1000
            self.task_latencies.append(total_elapsed_ms)
            self.total_completed_tasks += 1

            # Stage 6: Formulate Final Result
            synthesis = {
                "task_id": task_id,
                "session_id": session_id,
                "status": "SUCCESS" if not consensus_check["contradiction_detected"] else "VERIFICATION_WARNING",
                "category": category,
                "consensus_score": consensus_check["consensus_score"],
                "results": final_output_payload,
                "execution_timeline": execution_timeline,
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

    def get_system_telemetry(self) -> Dict[str, Any]:
        """Aggregate telemetry for Chat UI dashboard."""
        hw = self.hardware.get_telemetry()
        model_info = self.model_runner.get_info()
        bus_info = self.synapse_bus.get_telemetry()
        
        cpu_pct = psutil.cpu_percent(interval=None)
        avg_lat = (sum(self.task_latencies) / len(self.task_latencies)) if self.task_latencies else 0.0
        sorted_lats = sorted(self.task_latencies)
        p95_lat = sorted_lats[int(len(sorted_lats) * 0.95)] if len(sorted_lats) >= 20 else avg_lat

        return {
            "gpu": {
                "device_name": hw.device_name,
                "cuda_available": hw.cuda_available,
                "total_vram_mb": hw.total_mb,
                "allocated_vram_mb": hw.allocated_mb,
                "usable_headroom_mb": hw.free_usable_mb
            },
            "system": {
                "cpu_utilization_pct": cpu_pct,
                "free_ram_mb": hw.system_ram_free_mb
            },
            "model": model_info,
            "tasks": {
                "completed": self.total_completed_tasks,
                "blocked": self.total_blocked_tasks,
                "failed": self.total_failed_tasks,
                "avg_latency_ms": round(avg_lat, 2),
                "p95_latency_ms": round(p95_lat, 2)
            },
            "synapse": bus_info,
            "neurons_count": len(self.registry.list_neurons())
        }

    def close(self) -> None:
        """Release all resources and close database connections."""
        self.model_runner.unload_model()
        self.storage.close()
        self.synapse_bus.clear()
        self.hardware.purge_cache()
