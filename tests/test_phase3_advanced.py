"""
Unit & Integration Test Suite for PROJECT: NEURON 0.3.0 Phase 3 Capabilities
Tests:
- Adaptive Neural Routing
- Advanced Multi-Stage Reasoning & Syntax Self-Repair
- 4-Tier Memory Hierarchy & Multi-Factor Retrieval
- Extended Tool Intelligence (NumPy, RepoExplorer, DocumentIndexer)
- Autonomous Multi-Step Agent Execution & Cancellation
- Standardized Plugin Architecture & Security Permissions
- Self-Improvement Telemetry Loop
"""

import os
import tempfile
import pytest

from neuron.routing.router import AdaptiveRouter, TaskDifficulty
from neuron.reasoning.engine import AdvancedReasoningEngine
from neuron.memory.hierarchy import MemoryHierarchy
from neuron.tools.numpy_engine import NumPyEngine
from neuron.tools.repo_explorer import RepositoryExplorer
from neuron.tools.document_indexer import DocumentIndexer
from neuron.agent.planner import AutonomousAgent, TaskState
from neuron.plugins.base import PluginManager, PluginManifest, BasePlugin
from neuron.plugins.statistics_plugin import StatisticsPlugin
from neuron.learning.self_improvement import SelfImprovementEngine
from neuron.core.engine import NeuralCore


# 1. Test Adaptive Router
def test_adaptive_router_difficulty_and_routing():
    router = AdaptiveRouter()
    
    # Simple arithmetic
    dec_simple = router.route("Calculate 2 + 2", "MATH")
    assert dec_simple.difficulty == TaskDifficulty.SIMPLE
    assert "neuron_math_01" in dec_simple.required_neurons
    assert dec_simple.requires_planning is False

    # Complex composite task
    dec_complex = router.route(
        "A fleet travels 500 miles, calculate fuel and simulate routing algorithm in Python",
        "COMPOSITE"
    )
    assert dec_complex.difficulty == TaskDifficulty.COMPLEX
    assert dec_complex.requires_planning is True
    assert dec_complex.requires_consensus is True
    assert "neuron_coder_01" in dec_complex.required_neurons


# 2. Test Advanced Reasoning & Code Self-Repair
def test_reasoning_syntax_self_repair():
    engine = AdvancedReasoningEngine()
    
    # Broken python snippet missing colon
    broken_code = """def calculate_area(width, height)
    return width * height"""
    
    initial_results = {
        "code": {
            "synthesized_code": broken_code,
            "syntax_valid": False,
            "syntax_error": "expected ':'"
        }
    }
    
    res = engine.reason_and_verify("Write function", "CODE", "test_repair_1", initial_results)
    assert res.reflection_attempts == 1
    assert res.synthesis["code"]["syntax_valid"] is True
    assert len(res.error_corrections) == 1
    assert res.error_corrections[0]["fixed"] is True


# 3. Test 4-Tier Memory Hierarchy
def test_memory_hierarchy_storage_and_retrieval():
    mem = MemoryHierarchy(db_path=":memory:")
    
    # Store in episodic, semantic, and procedural
    mem.store("semantic", "Transformer Definition", "Self-attention architecture based on dot-product attention", ["ai", "architecture"])
    mem.store("procedural", "Quadratic Solver Procedure", "Isolate a,b,c then compute (-b +- sqrt(b^2 - 4ac)) / 2a", ["math"])
    mem.store("episodic", "Task 123", "User requested 25*40, solved via SymPy", ["math"])

    # Retrieve semantic knowledge
    results = mem.retrieve("What is transformer self-attention", tier="semantic")
    assert len(results) >= 1
    assert "Transformer Definition" in results[0]["title"]
    assert results[0]["score"] > 0.4

    # Test deduplication
    mid1 = mem.store("semantic", "Deduplication Test", "Content 1")
    mid2 = mem.store("semantic", "Deduplication Test", "Updated Content")
    assert mid1 == mid2

    mem.close()


# 4. Test NumPy Engine
def test_numpy_engine_computations():
    engine = NumPyEngine()
    
    # Descriptive stats
    stats = engine.descriptive_statistics([10.0, 20.0, 30.0, 40.0, 50.0])
    assert stats["success"] is True
    assert stats["mean"] == 30.0
    assert stats["median"] == 30.0
    assert stats["min"] == 10.0

    # Matrix multiplication
    m1 = [[1.0, 2.0], [3.0, 4.0]]
    m2 = [[2.0, 0.0], [1.0, 2.0]]
    mult = engine.matrix_multiply(m1, m2)
    assert mult["success"] is True
    assert mult["result"] == [[4.0, 4.0], [10.0, 8.0]]


# 5. Test Repository Explorer
def test_repository_explorer():
    res = RepositoryExplorer.scan_directory(".", max_depth=1)
    assert res["success"] is True
    assert res["total_files"] > 0


# 6. Test Document Indexer
def test_document_indexer():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("Section 1: NEURON Architecture\n\nSection 2: Synapse Protocol Details")
        temp_name = f.name

    indexer = DocumentIndexer()
    ingest_res = indexer.ingest_file(temp_name)
    assert ingest_res["success"] is True
    assert ingest_res["chunks_indexed"] == 2

    query_res = indexer.query_evidence("Synapse Protocol")
    assert query_res["found_citations"] >= 1
    os.remove(temp_name)


# 7. Test Autonomous Multi-Step Agent
def test_autonomous_agent_plan_and_execution():
    agent = AutonomousAgent()
    task = agent.create_plan("Audit repository syntax", target_dir=".")
    assert len(task.steps) == 4
    assert task.state == TaskState.PENDING

    # Execute Step 1
    step1_res = agent.execute_step(task.task_id)
    assert step1_res["success"] is True
    assert task.progress_pct == 25.0

    # Cancel task
    cancelled = agent.cancel_task(task.task_id)
    assert cancelled is True
    assert task.state == TaskState.CANCELLED


# 8. Test Plugin Architecture & Permissions
def test_plugin_manager_and_permissions():
    mgr = PluginManager()
    stats_plugin = StatisticsPlugin()
    
    # Register valid plugin
    reg_res = mgr.register_plugin(stats_plugin)
    assert reg_res["success"] is True

    # Execute capability
    exec_res = mgr.execute_plugin("statistics_core", "descriptive_stats", {"numbers": [2, 4, 6, 8]})
    assert exec_res["mean"] == 5.0

    # Disallow prohibited permissions
    class DangerousPlugin(BasePlugin):
        def __init__(self):
            manifest = PluginManifest("danger", "1.0", "Hacker", "RCE", ["rce"], permissions=["unrestricted_shell"])
            super().__init__(manifest)
        def initialize(self): return True
        def execute(self, a, p): return {}
        def shutdown(self): pass

    bad_reg = mgr.register_plugin(DangerousPlugin())
    assert bad_reg["success"] is False
    assert "prohibited permissions" in bad_reg["error"]


# 9. Test Self-Improvement Engine
def test_self_improvement_engine():
    engine = SelfImprovementEngine()
    
    # Record repetitive slow simple math
    for i in range(5):
        engine.observe_task(
            task_id=f"t_{i}",
            category="MATH",
            difficulty="simple",
            selected_neurons=["neuron_math_01", "neuron_planner_01"],
            duration_ms=65.0,
            verification_status="SUCCESS",
            consensus_score=1.0,
            reflection_attempts=0
        )

    proposals = engine.analyze_bottlenecks()
    assert len(proposals) >= 1
    assert "AdaptiveRouter" in proposals[0].rule_target
