"""
Adaptive Neural Routing Engine for PROJECT: NEURON
Evaluates task difficulty, predicts required specialist neurons and tools,
and minimizes unnecessary neuron activations.
"""

import time
import re
from enum import Enum
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field


class TaskDifficulty(str, Enum):
    SIMPLE = "simple"       # Sub-10ms direct tool / single neuron
    MODERATE = "moderate"   # Specialist + static verification
    COMPLEX = "complex"     # Multi-neuron DAG + consensus verification
    CRITICAL = "critical"   # Security guardrail / high risk


@dataclass
class RoutingDecision:
    prompt: str
    category: str
    difficulty: TaskDifficulty
    difficulty_score: float  # 0.0 to 1.0
    required_neurons: List[str]
    required_tools: List[str]
    requires_planning: bool
    requires_consensus: bool
    requires_knowledge_retrieval: bool
    decision_latency_ms: float
    confidence: float = 1.0
    reasoning: str = ""


class AdaptiveRouter:
    """
    Intelligent, difficulty-aware task router.
    Prevents indiscriminate activation of every neuron and chooses the optimal execution path.
    """

    def __init__(self):
        self.total_routing_decisions = 0
        self.total_routing_time_ms = 0.0
        self.activation_counts: Dict[str, int] = {}

    def compute_difficulty(self, prompt: str, category: str) -> float:
        """
        Computes normalized difficulty score (0.0 to 1.0) based on
        token length, domain overlap, syntactic complexity, and variable density.
        """
        score = 0.1
        tokens = prompt.split()
        num_tokens = len(tokens)

        # Length factor
        if num_tokens > 30:
            score += 0.25
        elif num_tokens > 15:
            score += 0.15

        # Domain overlap factor
        if category == "COMPOSITE":
            score += 0.40
        elif category in ["PLANNING", "REASONING"]:
            score += 0.30
        elif category in ["MATH", "CODE"]:
            score += 0.15

        # Mathematical complexity markers
        if re.search(r"(\^|\b(solve|equation|integral|derivative|matrix|polynomial)\b)", prompt, re.I):
            score += 0.20

        # Algorithmic complexity markers
        if re.search(r"\b(algorithm|simulate|optimize|analyze|refactor|test|benchmark|graph|tree)\b", prompt, re.I):
            score += 0.20

        return min(1.0, round(score, 2))

    def route(self, prompt: str, reflex_category: str) -> RoutingDecision:
        """
        Generates optimal routing decision for a given prompt and reflex classification.
        """
        start = time.perf_counter()
        prompt_lower = prompt.lower()
        
        # 1. Critical / Blocked
        if reflex_category == "BLOCKED":
            elapsed = (time.perf_counter() - start) * 1000
            return RoutingDecision(
                prompt=prompt,
                category="BLOCKED",
                difficulty=TaskDifficulty.CRITICAL,
                difficulty_score=1.0,
                required_neurons=["neuron_reflex_01"],
                required_tools=[],
                requires_planning=False,
                requires_consensus=False,
                requires_knowledge_retrieval=False,
                decision_latency_ms=round(elapsed, 2),
                confidence=1.0,
                reasoning="Security threat detected; immediate termination"
            )

        # 2. Difficulty Assessment
        diff_score = self.compute_difficulty(prompt, reflex_category)
        if diff_score < 0.35:
            difficulty = TaskDifficulty.SIMPLE
        elif diff_score < 0.70:
            difficulty = TaskDifficulty.MODERATE
        else:
            difficulty = TaskDifficulty.COMPLEX

        # 3. Neuron & Tool Selection based on difficulty
        required_neurons: List[str] = ["neuron_reflex_01"]
        required_tools: List[str] = []
        requires_planning = False
        requires_consensus = False
        requires_retrieval = False

        if reflex_category == "MATH":
            required_neurons.append("neuron_math_01")
            required_tools.append("sympy")
            if difficulty == TaskDifficulty.COMPLEX:
                requires_planning = True
                requires_consensus = True
            elif difficulty == TaskDifficulty.MODERATE:
                requires_consensus = True

        elif reflex_category == "CODE":
            required_neurons.append("neuron_coder_01")
            required_tools.extend(["ast_parser", "code_sandbox"])
            if difficulty in [TaskDifficulty.MODERATE, TaskDifficulty.COMPLEX]:
                requires_planning = True
                requires_consensus = True

        elif reflex_category == "COMPOSITE":
            required_neurons.extend(["neuron_planner_01", "neuron_math_01", "neuron_coder_01"])
            required_tools.extend(["sympy", "ast_parser", "code_sandbox"])
            requires_planning = True
            requires_consensus = True
            requires_retrieval = (diff_score > 0.8)

        elif reflex_category in ["KNOWLEDGE", "REASONING", "PLANNING"]:
            required_neurons.append("neuron_planner_01")
            requires_planning = True
            requires_retrieval = True
            if difficulty == TaskDifficulty.COMPLEX:
                requires_consensus = True

        # Track telemetry
        elapsed = (time.perf_counter() - start) * 1000
        self.total_routing_decisions += 1
        self.total_routing_time_ms += elapsed
        for nid in required_neurons:
            self.activation_counts[nid] = self.activation_counts.get(nid, 0) + 1

        return RoutingDecision(
            prompt=prompt,
            category=reflex_category,
            difficulty=difficulty,
            difficulty_score=diff_score,
            required_neurons=required_neurons,
            required_tools=required_tools,
            requires_planning=requires_planning,
            requires_consensus=requires_consensus,
            requires_knowledge_retrieval=requires_retrieval,
            decision_latency_ms=round(elapsed, 2),
            confidence=0.95 if difficulty == TaskDifficulty.SIMPLE else 0.88,
            reasoning=f"Difficulty {difficulty.value.upper()} ({diff_score}) -> Selected {len(required_neurons)} neurons, {len(required_tools)} tools"
        )

    def get_telemetry(self) -> Dict[str, Any]:
        """Return routing efficiency telemetry."""
        avg_lat = (self.total_routing_time_ms / self.total_routing_decisions) if self.total_routing_decisions > 0 else 0.0
        return {
            "total_routing_decisions": self.total_routing_decisions,
            "avg_routing_latency_ms": round(avg_lat, 2),
            "activation_counts": dict(self.activation_counts)
        }
