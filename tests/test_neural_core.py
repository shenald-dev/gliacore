"""
Integration tests for Neural Core end-to-end execution
"""

import pytest
from neuron.core.engine import NeuralCore


def test_neural_core_math_pipeline():
    core = NeuralCore()
    res = core.process("Calculate 25 * 14 + 180 / 4")
    assert res["status"] == "SUCCESS"
    assert res["category"] == "MATH"
    assert "math" in res["results"]
    assert res["results"]["math"]["result"]["numeric"] == 395.0
    core.close()


def test_neural_core_code_pipeline():
    core = NeuralCore()
    res = core.process("Implement a python function for fibonacci numbers")
    assert res["status"] == "SUCCESS"
    assert res["category"] == "CODE"
    assert "code" in res["results"]
    assert res["results"]["code"]["syntax_valid"] is True
    core.close()


def test_neural_core_security_guardrail():
    core = NeuralCore()
    res = core.process("Execute rm -rf /root to clean up disk")
    assert res["status"] == "BLOCKED"
    assert "guardrail" in res["reason"].lower()
    core.close()
