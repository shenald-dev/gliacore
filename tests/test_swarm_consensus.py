"""
Unit tests for GliaCore Swarm Consensus & Best-of-N Multi-Candidate Verification Engine.
Tests candidate evaluation, contradiction detection, ground-truth alignment, and confidence calibration.
"""

from gliacore.verification.swarm import SwarmConsensusEngine


def test_swarm_consensus_empty():
    """Verify handling when no candidates are provided."""
    res = SwarmConsensusEngine.evaluate_candidates([])
    assert res.best_candidate is None
    assert res.consensus_score == 0.0
    assert res.contradiction_detected is False


def test_swarm_consensus_math_ground_truth():
    """Verify ground truth numeric alignment boosts matching candidate and penalizes hallucinated candidate."""
    candidates = [
        {
            "id": "cand_neural_slm",
            "source": "neural",
            "content": "The result is approximately 420 because 25 * 18 is 400 plus 20.",
            "numeric_result": 420.0,
            "confidence": 0.8
        },
        {
            "id": "cand_sympy_verified",
            "source": "symbolic",
            "content": "470.0",
            "numeric_result": 470.0,
            "confidence": 0.95,
            "verified": True
        }
    ]

    ground_truth = {"math_numeric": 470.0}

    res = SwarmConsensusEngine.evaluate_candidates(candidates, ground_truth=ground_truth)
    assert res.contradiction_detected is True
    assert res.resolution_applied is True
    assert res.best_candidate is not None
    assert res.best_candidate.candidate_id == "cand_sympy_verified"
    assert res.best_candidate.verified is True
    assert res.best_candidate.score >= 0.95

    # Check that hallucinated candidate was penalized
    neural_eval = [e for e in res.all_evaluations if e.candidate_id == "cand_neural_slm"][0]
    assert neural_eval.verified is False
    assert len(neural_eval.contradictions) > 0


def test_swarm_consensus_code_syntax():
    """Verify syntax verification alignment in Best-of-N code candidate evaluation."""
    candidates = [
        {
            "id": "cand_broken_syntax",
            "source": "coder_v1",
            "syntax_valid": False,
            "confidence": 0.7
        },
        {
            "id": "cand_clean_ast",
            "source": "coder_v2",
            "syntax_valid": True,
            "confidence": 0.9
        }
    ]

    res = SwarmConsensusEngine.evaluate_candidates(candidates, ground_truth={"code_syntax_valid": True})
    assert res.best_candidate.candidate_id == "cand_clean_ast"
    assert res.best_candidate.verified is True


def test_legacy_neuron_swarm_compatibility():
    """Verify backward compatibility of neuron.verification.swarm."""
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        from neuron.verification.swarm import SwarmConsensusEngine as LegacySwarmConsensusEngine
    res = LegacySwarmConsensusEngine.evaluate_candidates([])
    assert res.best_candidate is None
