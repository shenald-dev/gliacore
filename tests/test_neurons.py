"""
Unit tests for Specialized Neurons & Verification Engine
"""

import pytest
from neuron.neurons.reflex import ReflexNeuron
from neuron.neurons.math_verifier import MathVerifierNeuron
from neuron.neurons.coder import CoderNeuron
from neuron.neurons.planner import PlannerNeuron
from neuron.verification.consensus import VerificationEngine


def test_reflex_neuron_classification():
    reflex = ReflexNeuron()
    
    math_task = reflex.run({"prompt": "Calculate the sum of 45 and 90"})
    assert math_task["result"]["category"] == "MATH"

    code_task = reflex.run({"prompt": "Implement a binary search function in Python"})
    assert code_task["result"]["category"] == "CODE"

    risky_task = reflex.run({"prompt": "Please run rm -rf / on the server"})
    assert risky_task["result"]["category"] == "BLOCKED"
    assert risky_task["result"]["risk_level"] == "HIGH"


def test_math_verifier_neuron():
    neuron = MathVerifierNeuron()
    res = neuron.run({"prompt": "What is 125 * 8?"})
    assert res["success"] is True
    math_data = res["result"]
    assert "result" in math_data
    assert math_data["result"]["numeric"] == 1000.0


def test_coder_neuron_synthesis_and_ast():
    neuron = CoderNeuron()
    res = neuron.run({"prompt": "Write a binary search algorithm", "run_tests": True})
    assert res["success"] is True
    data = res["result"]
    assert data["syntax_valid"] is True
    assert "binary_search" in data["structure"]["functions"]


def test_verification_engine_consensus():
    verifier = VerificationEngine()
    
    # Valid math artifact
    math_art = verifier.verify_artifact("math", {"result": {"success": True, "numeric": 42.0}})
    assert math_art["verified"] is True
    assert math_art["confidence"] == 1.0

    # Contradiction check
    consensus = verifier.detect_contradictions([math_art])
    assert consensus["contradiction_detected"] is False
    assert consensus["consensus_score"] == 1.0
