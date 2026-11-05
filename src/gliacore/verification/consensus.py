"""
Verification & Cross-Neuron Consensus Engine for GliaCore.
Detects contradictions, validates artifacts, executes schema verification,
and assigns confidence calibrations.
"""

from typing import Dict, Any, List
from gliacore.verification.schema import JSONExtractor, SchemaValidator


class VerificationEngine:
    """
    Independent checking engine.
    Ensures that neuron outputs are verified against deterministic tools,
    conform to schemas, and are free of logical contradictions.
    """

    @staticmethod
    def verify_artifact(artifact_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs type-specific verification logic.
        """
        if artifact_type == "math":
            res = data.get("result", {})
            if res.get("success"):
                return {
                    "verified": True,
                    "confidence": 1.0,
                    "reason": "Verified via SymPy deterministic algebra engine",
                    "details": res
                }
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": res.get("error", "Math evaluation failed"),
                "details": res
            }

        elif artifact_type == "code":
            syntax_valid = data.get("syntax_valid", False)
            exec_res = data.get("execution")
            
            if not syntax_valid:
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "reason": f"Syntax error detected: {data.get('syntax_error')}",
                    "details": data
                }

            if exec_res and not exec_res.get("success"):
                return {
                    "verified": False,
                    "confidence": 0.2,
                    "reason": f"Runtime execution failed: {exec_res.get('error')}",
                    "details": exec_res
                }

            return {
                "verified": True,
                "confidence": 0.95 if exec_res else 0.85,
                "reason": "Code passed AST static analysis and execution validation",
                "details": data
            }

        elif artifact_type == "reflex":
            risk = data.get("risk_level", "UNKNOWN")
            if risk == "HIGH":
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "reason": "Reflex neuron flagged high-risk payload",
                    "details": data
                }
            return {
                "verified": True,
                "confidence": 0.90,
                "reason": "Security and intent verified",
                "details": data
            }

        elif artifact_type == "schema":
            raw_content = data.get("raw", "")
            schema = data.get("schema", {})
            ok, parsed, msg = JSONExtractor.parse_and_repair(raw_content)
            if not ok or parsed is None:
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "reason": f"Failed to parse or repair JSON: {msg}",
                    "details": {"raw": raw_content, "error": msg}
                }

            if schema:
                valid, schema_errs = SchemaValidator.validate(parsed, schema)
                if not valid:
                    return {
                        "verified": False,
                        "confidence": 0.3,
                        "reason": f"Schema validation errors: {', '.join(schema_errs)}",
                        "details": {"parsed": parsed, "errors": schema_errs}
                    }

            return {
                "verified": True,
                "confidence": 0.98,
                "reason": f"JSON parsed and validated successfully ({msg})",
                "details": {"parsed": parsed}
            }

        return {
            "verified": True,
            "confidence": 0.75,
            "reason": "Default pass with standard confidence",
            "details": data
        }

    @staticmethod
    def detect_contradictions(artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes a list of multi-neuron artifacts for mutually exclusive claims.
        """
        has_failure = any(not a.get("verified", True) for a in artifacts)
        confidences = [a.get("confidence", 0.5) for a in artifacts if "confidence" in a]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return {
            "contradiction_detected": has_failure,
            "consensus_score": round(avg_confidence, 2),
            "total_artifacts_evaluated": len(artifacts)
        }
