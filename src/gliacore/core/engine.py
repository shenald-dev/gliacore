"""
NEURAL CORE 0.3.0 — Advanced Collaborative Intelligence Orchestrator
Integrates:
- Adaptive Neural Router (difficulty-aware, confidence-calibrated)
- Advanced Reasoning Engine (generate-and-verify, reflection, self-repair)
- 4-Tier Memory Hierarchy (working, episodic, semantic, procedural)
- Autonomous Multi-Step Agent
- Extensible Plugin Architecture
- Self-Improvement Telemetry Loop
"""

import time
import uuid
import json
import psutil
from typing import Dict, Any, List, Optional

from gliacore.core.hardware import HardwareSupervisor
from gliacore.core.registry import NeuronRegistry
from gliacore.core.model_runner import ModelRunner
from gliacore.synapse.bus import SynapseBus
from gliacore.memory.working import WorkingMemory
from gliacore.memory.storage import KnowledgeStorage
from gliacore.memory.hierarchy import MemoryHierarchy
from gliacore.verification.consensus import VerificationEngine

from gliacore.neurons.reflex import ReflexNeuron
from gliacore.neurons.planner import PlannerNeuron
from gliacore.neurons.math_verifier import MathVerifierNeuron
from gliacore.neurons.coder import CoderNeuron

from gliacore.routing.router import AdaptiveRouter
from gliacore.reasoning.engine import AdvancedReasoningEngine
from gliacore.agent.planner import AutonomousAgent
from gliacore.plugins.base import PluginManager
from gliacore.plugins.statistics_plugin import StatisticsPlugin
from gliacore.tools.document_indexer import DocumentIndexer
from gliacore.learning.self_improvement import SelfImprovementEngine
from gliacore.tools.registry import ToolRegistry
from gliacore.verification.swarm import SwarmConsensusEngine


class NeuralCore:
    """
    The advanced brain of PROJECT: NEURON 0.3.0.
    Coordinates adaptive routing, multi-stage reasoning, 4-tier memory,
    autonomous agent planning, and self-improving execution.
    """

    def __init__(self, db_path: Optional[str] = None, memory_db_path: Optional[str] = None, auto_load_model: bool = False):
        import os
        if db_path is None:
            if os.path.exists("gliacore_store.db"):
                db_path = "gliacore_store.db"
            elif os.path.exists("neuron_store.db"):
                db_path = "neuron_store.db"
            else:
                db_path = "gliacore_store.db"

        if memory_db_path is None:
            if os.path.exists("gliacore_memory.db"):
                memory_db_path = "gliacore_memory.db"
            elif os.path.exists("neuron_memory.db"):
                memory_db_path = "neuron_memory.db"
            else:
                memory_db_path = "gliacore_memory.db"
        self.hardware = HardwareSupervisor()
        self.synapse_bus = SynapseBus()
        self.registry = NeuronRegistry()
        self.storage = KnowledgeStorage(db_path=db_path)
        self.memory = MemoryHierarchy(db_path=memory_db_path)
        self.verifier = VerificationEngine()
        self.model_runner = ModelRunner(hardware_supervisor=self.hardware)
        if auto_load_model and os.environ.get("GLIACORE_NO_AUTOLOAD") != "1" and os.environ.get("NEURON_NO_AUTOLOAD") != "1":
            try:
                self.model_runner.load_model("qwen-0.5b")
            except Exception:
                pass

        # Advanced Phase 3 Subsystems
        self.router = AdaptiveRouter()
        self.reasoning_engine = AdvancedReasoningEngine(max_reflection_retries=2)
        self.agent = AutonomousAgent()
        self.document_indexer = DocumentIndexer(storage=self.storage)
        self.self_improvement = SelfImprovementEngine()
        self.plugin_manager = PluginManager()
        self.tool_registry = ToolRegistry()
        self.swarm_verifier = SwarmConsensusEngine()

        # Operational metrics
        self.total_completed_tasks: int = 0
        self.total_failed_tasks: int = 0
        self.total_blocked_tasks: int = 0
        self.task_latencies: List[float] = []

        # Initialize neuron fleet & default plugins
        self._init_neuron_fleet()
        self._init_plugins()
        self._register_default_tools()

    def _init_neuron_fleet(self) -> None:
        """Instantiate and wire neurons to the Synapse communication bus."""
        self.reflex_neuron = ReflexNeuron(bus=self.synapse_bus)
        self.planner_neuron = PlannerNeuron(bus=self.synapse_bus)
        self.math_neuron = MathVerifierNeuron(bus=self.synapse_bus)
        self.coder_neuron = CoderNeuron(bus=self.synapse_bus, model_runner=self.model_runner)

        self.registry.register(self.reflex_neuron)
        self.registry.register(self.planner_neuron)
        self.registry.register(self.math_neuron)
        self.registry.register(self.coder_neuron)

    def _init_plugins(self) -> None:
        """Load standard plugins."""
        try:
            stats_plugin = StatisticsPlugin()
            self.plugin_manager.register_plugin(stats_plugin)
        except Exception:
            pass

    def process(self, prompt: str, task_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Adaptive Multi-Stage Collective Intelligence Pipeline:
        1. VRAM/RAM Pre-flight Check
        2. Reflex Intent & Security Screening
        3. Adaptive Difficulty & Routing Decision
        4. Episodic & Semantic Memory Context Retrieval
        5. Cognitive Planning & Selective Neuron Execution
        6. Generate-and-Verify Reflection Loop (Self-Repair)
        7. Consensus & Contradiction Verification
        8. Memory Consolidation & Self-Improvement Telemetry
        """
        task_id = task_id or str(uuid.uuid4())
        working_mem = WorkingMemory(task_id=task_id)
        start_time = time.perf_counter()
        execution_timeline: List[Dict[str, Any]] = []

        with self.hardware.memory_tracer(label=f"task_{task_id[:8]}") as mem_stats:
            # Stage 1: Reflex & Security Screening
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

            # Stage 2: Adaptive Difficulty & Routing Decision
            t0 = time.perf_counter()
            route_decision = self.router.route(prompt, category)
            t_route = round((time.perf_counter() - t0) * 1000, 2)

            execution_timeline.append({
                "stage": "Adaptive Neural Routing",
                "neuron": "adaptive_router",
                "state": "completed",
                "duration_ms": t_route,
                "output": {
                    "difficulty": route_decision.difficulty.value,
                    "difficulty_score": route_decision.difficulty_score,
                    "required_neurons": route_decision.required_neurons,
                    "required_tools": route_decision.required_tools
                }
            })

            # Stage 3: Episodic & Semantic Memory Retrieval
            t0 = time.perf_counter()
            relevant_experiences = self.memory.retrieve(prompt, limit=2)
            t_mem = round((time.perf_counter() - t0) * 1000, 2)
            working_mem.set_state("retrieved_memory", relevant_experiences)

            execution_timeline.append({
                "stage": "4-Tier Memory Retrieval",
                "neuron": "memory_hierarchy",
                "state": "completed",
                "duration_ms": t_mem,
                "output": {"retrieved_memories": len(relevant_experiences)}
            })

            # Stage 4: Cognitive Planning (Activated only when difficulty/category requires it)
            planner_res = None
            if route_decision.requires_planning:
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

            # Stage 5: Selective Specialist Execution via Synapses
            intermediate_artifacts: List[Dict[str, Any]] = []
            raw_specialist_output: Dict[str, Any] = {}

            # Execute Math Neuron if selected by router
            if "neuron_math_01" in route_decision.required_neurons:
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
                raw_specialist_output["math"] = math_res["result"]

                execution_timeline.append({
                    "stage": "Mathematical Reasoning (SymPy)",
                    "neuron": self.math_neuron.neuron_id,
                    "state": "completed" if math_verif["verified"] else "failed",
                    "duration_ms": t_math,
                    "output": math_res["result"]
                })

            # Execute Coder Neuron if selected by router
            if "neuron_coder_01" in route_decision.required_neurons:
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
                raw_specialist_output["code"] = code_res["result"]

                execution_timeline.append({
                    "stage": "Code Synthesis & AST Validation",
                    "neuron": self.coder_neuron.neuron_id,
                    "state": "completed" if code_verif["verified"] else "failed",
                    "duration_ms": t_code,
                    "output": {"syntax_valid": code_res["result"].get("syntax_valid")}
                })

            # GPU-Accelerated Synthesis & Explanation Layer
            if self.model_runner.is_real_weights and "reasoning" not in raw_specialist_output:
                t0 = time.perf_counter()
                if "math" in raw_specialist_output:
                    m = raw_specialist_output["math"]
                    calc_val = m.get("result", {}).get("numeric", m.get("result", {}).get("exact", m.get("result", {}).get("solutions")))
                    math_expl_prompt = (
                        f"Explain this mathematical problem and step-by-step derivation concisely:\n"
                        f"Problem: {prompt}\n"
                        f"Exact Verified Result: {calc_val}\n"
                        f"Provide the step-by-step mathematical reasoning."
                    )
                    gen_res = self.model_runner.generate(math_expl_prompt, max_new_tokens=256)
                    t_gen = round((time.perf_counter() - t0) * 1000, 2)
                    raw_specialist_output["reasoning"] = {
                        "text": gen_res["text"],
                        "mode": gen_res["mode"],
                        "tokens": gen_res["tokens_generated"]
                    }
                    execution_timeline.append({
                        "stage": "GPU Mathematical Derivation & Explanation",
                        "neuron": "model_runner",
                        "state": "completed",
                        "duration_ms": t_gen,
                        "output": {"mode": gen_res["mode"], "tokens": gen_res["tokens_generated"]}
                    })
                elif "code" in raw_specialist_output:
                    c = raw_specialist_output["code"]
                    code_text = c.get("synthesized_code", "")
                    code_expl_prompt = (
                        f"Provide a brief 2-3 sentence overview of this implementation, including its time and space complexity:\n"
                        f"```python\n{code_text[:350]}\n```"
                    )
                    gen_res = self.model_runner.generate(code_expl_prompt, max_new_tokens=256)
                    t_gen = round((time.perf_counter() - t0) * 1000, 2)
                    raw_specialist_output["reasoning"] = {
                        "text": gen_res["text"],
                        "mode": gen_res["mode"],
                        "tokens": gen_res["tokens_generated"]
                    }
                    execution_timeline.append({
                        "stage": "GPU Code Explanation & Complexity",
                        "neuron": "model_runner",
                        "state": "completed",
                        "duration_ms": t_gen,
                        "output": {"mode": gen_res["mode"], "tokens": gen_res["tokens_generated"]}
                    })

            # General reasoning / Model generation fallback
            if category in ["REASONING", "KNOWLEDGE", "PLANNING"] or not raw_specialist_output:
                t0 = time.perf_counter()
                gen_res = self.model_runner.generate(prompt)
                t_gen = round((time.perf_counter() - t0) * 1000, 2)
                raw_specialist_output["reasoning"] = {
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

            # Stage 6: Advanced Multi-Stage Reasoning & Reflection (Generate-and-Verify)
            t0 = time.perf_counter()
            reasoning_eval = self.reasoning_engine.reason_and_verify(
                prompt=prompt,
                category=category,
                task_id=task_id,
                initial_results=raw_specialist_output
            )
            t_reason = round((time.perf_counter() - t0) * 1000, 2)

            if reasoning_eval.reflection_attempts > 0:
                execution_timeline.append({
                    "stage": "Cognitive Reflection & Self-Repair",
                    "neuron": "reasoning_engine",
                    "state": "completed",
                    "duration_ms": t_reason,
                    "output": {
                        "reflection_attempts": reasoning_eval.reflection_attempts,
                        "error_corrections": reasoning_eval.error_corrections
                    }
                })

            # Stage 7: Consensus Verification (Only when required)
            consensus_score = reasoning_eval.confidence_score
            has_contradiction = not reasoning_eval.verified

            if route_decision.requires_consensus:
                t0 = time.perf_counter()
                consensus_check = self.verifier.detect_contradictions(intermediate_artifacts)
                t_consensus = round((time.perf_counter() - t0) * 1000, 2)
                consensus_score = min(consensus_score, consensus_check["consensus_score"])
                has_contradiction = has_contradiction or consensus_check["contradiction_detected"]

                execution_timeline.append({
                    "stage": "Consensus & Contradiction Verification",
                    "neuron": "verification_engine",
                    "state": "completed" if not has_contradiction else "warning",
                    "duration_ms": t_consensus,
                    "output": consensus_check
                })

            total_elapsed_ms = (time.perf_counter() - start_time) * 1000
            self.task_latencies.append(total_elapsed_ms)
            self.total_completed_tasks += 1

            # Stage 8: Experience Consolidation & Self-Improvement Telemetry
            status_str = "SUCCESS" if not has_contradiction else "VERIFICATION_WARNING"
            
            # Store validated experience in Episodic Memory
            self.memory.store(
                tier="episodic",
                title=f"Task: {prompt[:40]}",
                content=json.dumps({"prompt": prompt, "results": reasoning_eval.synthesis}),
                tags=[category, route_decision.difficulty.value],
                reliability=consensus_score,
                metadata={"task_id": task_id, "duration_ms": total_elapsed_ms}
            )

            # Record in Long-term task history
            plan_summary = str(planner_res["result"].get("stages", [])) if planner_res else "Direct Routing"
            self.storage.record_task_history(
                task_id=task_id,
                prompt=prompt,
                category=category,
                plan=plan_summary,
                output=str(reasoning_eval.synthesis),
                status=status_str,
                latency_ms=total_elapsed_ms
            )

            # Log to Self-Improvement Engine
            self.self_improvement.observe_task(
                task_id=task_id,
                category=category,
                difficulty=route_decision.difficulty.value,
                selected_neurons=route_decision.required_neurons,
                duration_ms=total_elapsed_ms,
                verification_status=status_str,
                consensus_score=consensus_score,
                reflection_attempts=reasoning_eval.reflection_attempts
            )

            # Formulate Final Result
            synthesis = {
                "task_id": task_id,
                "session_id": session_id,
                "status": status_str,
                "category": category,
                "difficulty": route_decision.difficulty.value,
                "difficulty_score": route_decision.difficulty_score,
                "consensus_score": consensus_score,
                "results": reasoning_eval.synthesis,
                "reflection_repairs": reasoning_eval.error_corrections,
                "execution_timeline": execution_timeline,
                "working_memory": working_mem.summary(),
                "synapse_telemetry": self.synapse_bus.get_telemetry(),
                "hardware_telemetry": mem_stats,
                "total_latency_ms": round(total_elapsed_ms, 2)
            }

            return synthesis


    def process_stream(self, prompt: str, task_id: Optional[str] = None, session_id: Optional[str] = None):
        """
        Event-driven streaming execution generator.
        Yields stage transition events, token streams, and final synthesis payload.
        """
        task_id = task_id or str(uuid.uuid4())
        start_time = time.perf_counter()

        # Stage 1: Reflex & Security Screening
        t0 = time.perf_counter()
        reflex_res = self.reflex_neuron.run({"prompt": prompt})
        t_reflex = round((time.perf_counter() - t0) * 1000, 2)
        category = reflex_res["result"].get("category", "GENERAL")
        is_blocked = (category == "BLOCKED")

        yield {
            "event": "stage",
            "stage": "Reflex Screening & Security",
            "neuron": self.reflex_neuron.neuron_id,
            "state": "blocked" if is_blocked else "completed",
            "duration_ms": t_reflex,
            "output": reflex_res["result"]
        }

        if is_blocked:
            self.total_blocked_tasks += 1
            total_elapsed_ms = (time.perf_counter() - start_time) * 1000
            yield {
                "event": "done",
                "task_id": task_id,
                "session_id": session_id,
                "status": "BLOCKED",
                "reason": reflex_res["result"].get("reason"),
                "results": {"blocked": True, "reason": reflex_res["result"].get("reason")},
                "total_latency_ms": round(total_elapsed_ms, 2),
                "response_markdown": f"**Execution Blocked by Safety Guardrail**\n\nReason: {reflex_res['result'].get('reason')}"
            }
            return

        # Stage 2: Adaptive Routing
        t0 = time.perf_counter()
        route_decision = self.router.route(prompt, category)
        t_route = round((time.perf_counter() - t0) * 1000, 2)

        yield {
            "event": "stage",
            "stage": "Adaptive Neural Routing",
            "neuron": "adaptive_router",
            "state": "completed",
            "duration_ms": t_route,
            "output": {
                "difficulty": route_decision.difficulty.value,
                "difficulty_score": route_decision.difficulty_score,
                "required_neurons": route_decision.required_neurons,
                "required_tools": route_decision.required_tools
            }
        }

        # Stage 3: Memory Retrieval
        t0 = time.perf_counter()
        relevant_experiences = self.memory.retrieve(prompt, limit=2)
        t_mem = round((time.perf_counter() - t0) * 1000, 2)

        yield {
            "event": "stage",
            "stage": "4-Tier Memory Retrieval",
            "neuron": "memory_hierarchy",
            "state": "completed",
            "duration_ms": t_mem,
            "output": {"retrieved_memories": len(relevant_experiences)}
        }

        # Stage 4: Cognitive Planning if required
        if route_decision.requires_planning:
            t0 = time.perf_counter()
            planner_res = self.planner_neuron.run({"prompt": prompt, "category": category})
            t_plan = round((time.perf_counter() - t0) * 1000, 2)
            yield {
                "event": "stage",
                "stage": "Cognitive Planning",
                "neuron": self.planner_neuron.neuron_id,
                "state": "completed",
                "duration_ms": t_plan,
                "output": planner_res["result"]
            }

        # Execute standard pipeline to obtain full verified results
        final_result = self.process(prompt, task_id=task_id, session_id=session_id)

        # Stream reasoning / explanation tokens
        reasoning_text = ""
        results = final_result.get("results", {})
        if "reasoning" in results and isinstance(results["reasoning"], dict):
            reasoning_text = results["reasoning"].get("text", "")

        if reasoning_text:
            chunks = reasoning_text.split(" ")
            for idx, chunk in enumerate(chunks):
                token = chunk + (" " if idx < len(chunks) - 1 else "")
                yield {
                    "event": "token",
                    "token": token
                }

        # Final completion event
        yield {
            "event": "done",
            "task_id": task_id,
            "session_id": session_id,
            "status": final_result["status"],
            "category": final_result["category"],
            "difficulty": final_result["difficulty"],
            "consensus_score": final_result["consensus_score"],
            "total_latency_ms": final_result["total_latency_ms"],
            "results": final_result["results"],
            "reflection_repairs": final_result["reflection_repairs"],
            "execution_timeline": final_result["execution_timeline"]
        }

    def get_system_telemetry(self) -> Dict[str, Any]:
        """Aggregate telemetry for Chat UI dashboard."""
        hw = self.hardware.get_telemetry()
        model_info = self.model_runner.get_info()
        bus_info = self.synapse_bus.get_telemetry()
        router_info = self.router.get_telemetry()
        improvement_info = self.self_improvement.get_insights()

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
            "router": router_info,
            "synapse": bus_info,
            "improvement": improvement_info,
            "plugins": self.plugin_manager.list_plugins(),
            "neurons_count": len(self.registry.list_neurons())
        }

    def _register_default_tools(self) -> None:
        """Register default ecosystem tools into the dynamic tool registry."""
        def math_solve(expression: str) -> Dict[str, Any]:
            """Evaluate mathematical expression or equation using SymPy."""
            res = self.math_neuron.run({"prompt": expression}).get("result", {})
            return res.get("result", res)

        def code_run(code: str, timeout_sec: float = 5.0) -> Dict[str, Any]:
            """Execute Python code in isolated AST-screened sandbox."""
            return self.coder_neuron.run({"code": code, "run_tests": True, "timeout_sec": timeout_sec}).get("result", {})

        def memory_query(query: str, limit: int = 5) -> List[Dict[str, Any]]:
            """Search episodic and semantic memory hierarchy."""
            return self.memory.retrieve(query, limit=limit)

        self.tool_registry.register_tool(
            name="math_solve",
            handler=math_solve,
            description="Evaluate mathematical expression or algebraic equation with exact SymPy CAS."
        )
        self.tool_registry.register_tool(
            name="code_run",
            handler=code_run,
            description="Execute Python code snippet in an isolated sandbox with AST verification."
        )
        self.tool_registry.register_tool(
            name="memory_query",
            handler=memory_query,
            description="Search 4-tier persistent memory for related experiences or facts."
        )

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via the dynamic tool registry."""
        return self.tool_registry.execute_tool(name, arguments)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools registered in the dynamic registry."""
        return [t.to_mcp_dict() for t in self.tool_registry.list_tools()]

    def close(self) -> None:
        """Release all resources and close database connections."""
        self.model_runner.unload_model()
        self.memory.close()
        self.storage.close()
        self.synapse_bus.clear()
        self.hardware.purge_cache()


# GliaCore Brand Identity Alias
GliaCore = NeuralCore
