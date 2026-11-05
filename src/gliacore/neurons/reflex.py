"""
Reflex & Guardrail Neuron for PROJECT: NEURON
Hardened semantic intent classifier, prompt injection blocker, and risk assessor.
"""

from typing import Dict, Any, List
import re
import base64
from gliacore.neurons.base import BaseNeuron
from gliacore.synapse.bus import SynapseBus

# High-risk destructive system commands across Linux, Windows, PowerShell
DESTRUCTIVE_PATTERNS = [
    r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+|--recursive\s+).*",
    r"rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)+",
    r"del\s+/[fFqsS]\s+",
    r"rmdir\s+/[sS]\s+",
    r"powershell.*(remove-item|start-process|stop-computer|restart-computer)",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # fork bomb
    r"DROP\s+(DATABASE|TABLE|SCHEMA)",
    r"__import__\s*\(\s*['\"]os['\"]\s*\)",
    r"(os|shutil)\.(system|rmtree|remove|unlink|popen)",
    r"(cat|type)\s+.*(shadow|sam|config[\\/]sam|passwd)",
]

# Prompt injection & jailbreak patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"you\s+are\s+now\s+(unconstrained|unfiltered|in\s+developer\s+mode|jailbroken)",
    r"disregard\s+(the\s+)?system\s+prompt",
    r"hypothetical\s+fictional\s+scenario\s+where\s+security\s+rules\s+are\s+disabled",
]


class ReflexNeuron(BaseNeuron):
    """
    Sub-millisecond reflex and security screening unit.
    Normalizes whitespace, decodes Base64 payloads, detects prompt injection,
    and screens high-risk commands before any downstream execution occurs.
    """

    def __init__(self, bus: SynapseBus = None):
        super().__init__(
            neuron_id="neuron_reflex_01",
            name="Reflex & Guardrail Neuron",
            specialization="reflex",
            bus=bus
        )

    def _screen_text(self, text: str) -> bool:
        """Evaluate text against security and prompt injection patterns."""
        normalized = re.sub(r"\s+", " ", text).strip()
        for pat in DESTRUCTIVE_PATTERNS + PROMPT_INJECTION_PATTERNS:
            if re.search(pat, normalized, re.IGNORECASE):
                return True
        return False

    def execute(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task_payload.get("prompt", "").strip()

        # 1. Primary Text Screening
        if self._screen_text(prompt):
            return {
                "category": "BLOCKED",
                "risk_level": "HIGH",
                "target_neurons": [],
                "reason": "Security guardrail triggered by high-risk payload or command injection"
            }

        # 2. Base64 Obfuscation Inspection
        b64_candidates = re.findall(r"[A-Za-z0-9+/]{12,}={0,2}", prompt)
        for cand in b64_candidates:
            try:
                decoded = base64.b64decode(cand).decode("utf-8", errors="ignore")
                if len(decoded) > 3 and self._screen_text(decoded):
                    return {
                        "category": "BLOCKED",
                        "risk_level": "HIGH",
                        "target_neurons": [],
                        "reason": "Security guardrail triggered by encoded malicious payload"
                    }
            except Exception:
                pass

        # 3. Semantic Intent Categorization
        prompt_lower = prompt.lower()
        has_math = any(kw in prompt_lower for kw in [
            "calculate", "solve", "equation", "math", "derive", "integral", "sum of",
            "multiply", "divide", "+", "-", "*", "/", "=", "^", "sqrt", "evaluate", "compute"
        ]) and bool(re.search(r"\d+", prompt))

        has_code = any(kw in prompt_lower for kw in [
            "def ", "function", "class ", "python", "code", "algorithm", "implement",
            "binary search", "regex", "script", "return ", "syntax", "write code", "analyze"
        ])

        has_planning = any(kw in prompt_lower for kw in [
            "design a", "plan an", "architecture", "stages", "workflow", "roadmap", "pipeline"
        ])

        has_knowledge = any(kw in prompt_lower for kw in [
            "what is", "who is", "explain", "history", "documentation", "lookup", "retrieve",
            "tell me about", "describe"
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
        elif has_planning:
            category = "PLANNING"
            target_neurons = ["neuron_planner_01"]
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
