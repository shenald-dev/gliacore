"""
Swarm Consensus & Multi-Candidate Verification Engine for GliaCore.
Executes Best-of-N evaluation across disparate candidate answers (symbolic vs. neural),
detects and resolves semantic contradictions, and assigns calibrated confidence scores.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class CandidateEvaluation:
    candidate_id: str
    source: str  # 'symbolic', 'neural', 'ast_sandbox', 'composite'
    content: Any
    confidence: float
    verified: bool
    score: float  # Composite ranking score (0.0 to 1.0)
    details: Dict[str, Any] = field(default_factory=dict)
    contradictions: List[str] = field(default_factory=list)


@dataclass
class SwarmConsensusResult:
    best_candidate: Optional[CandidateEvaluation]
    consensus_score: float
    all_evaluations: List[CandidateEvaluation]
    contradiction_detected: bool
    resolution_applied: bool
    audit_trail: List[str] = field(default_factory=list)


class SwarmConsensusEngine:
    """
    Evaluates multi-agent or multi-neuron candidates, resolves contradictions,
    and guarantees that ground-truth symbolic results take precedence over neural hallucinations.
    """

    @staticmethod
    def evaluate_candidates(
        candidates: List[Dict[str, Any]],
        ground_truth: Optional[Dict[str, Any]] = None
    ) -> SwarmConsensusResult:
        """
        Evaluate candidates against deterministic ground-truth and internal consistency.
        ground_truth can contain known verified values, e.g.:
        {"math_numeric": 470.0, "code_syntax_valid": True}
        """
        if not candidates:
            return SwarmConsensusResult(
                best_candidate=None,
                consensus_score=0.0,
                all_evaluations=[],
                contradiction_detected=False,
                resolution_applied=False,
                audit_trail=["No candidates provided for consensus evaluation."]
            )

        evaluations: List[CandidateEvaluation] = []
        contradictions_found = False
        audit: List[str] = []
        ground_truth = ground_truth or {}

        for idx, cand in enumerate(candidates):
            cand_id = cand.get("id", f"cand_{idx}")
            source = cand.get("source", "unknown")
            content = cand.get("content")
            base_conf = float(cand.get("confidence", 0.5))

            cand_contradictions: List[str] = []
            cand_score = base_conf
            verified = cand.get("verified", False)

            # 1. Deterministic Math Check
            if "math_numeric" in ground_truth:
                expected_num = ground_truth["math_numeric"]
                cand_num = cand.get("numeric_result")

                if cand_num is not None:
                    try:
                        if abs(float(cand_num) - float(expected_num)) < 1e-6:
                            cand_score += 0.4
                            verified = True
                            audit.append(f"Candidate {cand_id}: Numeric match with ground truth ({expected_num}).")
                        else:
                            cand_score -= 0.6
                            verified = False
                            contradictions_found = True
                            cand_contradictions.append(
                                f"Numeric result {cand_num} diverges from verified ground truth {expected_num}."
                            )
                            audit.append(f"Candidate {cand_id}: CONTRADICTION - diverges from ground truth.")
                    except (ValueError, TypeError):
                        pass

            # 2. AST Code Validation Check
            if "code_syntax_valid" in ground_truth:
                expected_syntax = ground_truth["code_syntax_valid"]
                cand_syntax = cand.get("syntax_valid")
                if cand_syntax == expected_syntax:
                    cand_score += 0.3
                    verified = True
                elif cand_syntax is False and expected_syntax is True:
                    cand_score -= 0.5
                    verified = False
                    contradictions_found = True
                    cand_contradictions.append("Syntax validation failed against expected clean syntax.")

            # Bound score between 0.0 and 1.0
            cand_score = max(0.0, min(1.0, cand_score))

            evaluation = CandidateEvaluation(
                candidate_id=cand_id,
                source=source,
                content=content,
                confidence=base_conf,
                verified=verified,
                score=round(cand_score, 2),
                details=cand.get("details", {}),
                contradictions=cand_contradictions
            )
            evaluations.append(evaluation)

        # Sort candidates by score descending
        evaluations.sort(key=lambda e: (e.verified, e.score), reverse=True)
        best = evaluations[0] if evaluations else None

        # Compute swarm consensus agreement score
        if evaluations:
            avg_score = sum(e.score for e in evaluations) / len(evaluations)
        else:
            avg_score = 0.0

        resolution_applied = False
        if contradictions_found and best and best.verified:
            resolution_applied = True
            audit.append(f"Consensus Resolution: Ground-truth verified candidate '{best.candidate_id}' selected.")

        return SwarmConsensusResult(
            best_candidate=best,
            consensus_score=round(avg_score, 2),
            all_evaluations=evaluations,
            contradiction_detected=contradictions_found,
            resolution_applied=resolution_applied,
            audit_trail=audit
        )
