"""
Comprehensive Unit Tests for GliaCore Schema-Constrained Decoding and JSON Auto-Repair Engine.
Tests extraction from raw LLM outputs, markdown code fence parsing, heuristic syntactic repairs,
lightweight JSON schema validation, and consensus verification engine integration.
"""

from gliacore.verification.schema import JSONExtractor, SchemaValidator
from gliacore.verification.consensus import VerificationEngine


def test_json_extractor_clean():
    """Verify parsing clean JSON strings without any modification."""
    clean = '{"status": "ok", "count": 42}'
    ok, parsed, _ = JSONExtractor.parse_and_repair(clean)
    assert ok is True
    assert parsed == {"status": "ok", "count": 42}


def test_json_extractor_markdown_fences():
    """Verify extracting JSON enclosed inside ```json ... ``` code blocks."""
    llm_output = """Here is the result of your analysis:

```json
{
  "task": "optimize_query",
  "confidence": 0.95,
  "recommendations": ["use_index", "limit_rows"]
}
```

Hope that helps!"""

    ok, parsed, _ = JSONExtractor.parse_and_repair(llm_output)
    assert ok is True
    assert parsed["task"] == "optimize_query"
    assert parsed["confidence"] == 0.95
    assert len(parsed["recommendations"]) == 2


def test_json_repair_python_literals():
    """Verify repairing Python literals (True, False, None) into valid JSON (true, false, null)."""
    malformed = '{"is_active": True, "is_deleted": False, "extra_info": None}'
    ok, parsed, msg = JSONExtractor.parse_and_repair(malformed)
    assert ok is True
    assert parsed["is_active"] is True
    assert parsed["is_deleted"] is False
    assert parsed["extra_info"] is None


def test_json_repair_trailing_commas():
    """Verify removing trailing commas in objects and arrays."""
    malformed = '{"items": [1, 2, 3,], "config": {"timeout": 30,},}'
    ok, parsed, msg = JSONExtractor.parse_and_repair(malformed)
    assert ok is True
    assert parsed["items"] == [1, 2, 3]
    assert parsed["config"]["timeout"] == 30


def test_json_repair_single_quotes():
    """Verify repairing single quotes into valid JSON double quotes."""
    malformed = "{'model': 'qwen-0.5b', 'temperature': 0.7, 'tags': ['fast', 'edge']}"
    ok, parsed, msg = JSONExtractor.parse_and_repair(malformed)
    assert ok is True
    assert parsed["model"] == "qwen-0.5b"
    assert parsed["tags"] == ["fast", "edge"]


def test_schema_validator_types():
    """Verify SchemaValidator checks property types correctly."""
    schema = {
        "type": "object",
        "required": ["name", "age", "is_member", "scores"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "is_member": {"type": "boolean"},
            "scores": {"type": "array"}
        }
    }

    valid_data = {
        "name": "Alice",
        "age": 30,
        "is_member": True,
        "scores": [95, 98]
    }
    valid, errors = SchemaValidator.validate(valid_data, schema)
    assert valid is True
    assert len(errors) == 0

    invalid_data = {
        "name": "Bob",
        "age": "thirty",  # wrong type
        # is_member missing
        "scores": "not an array"  # wrong type
    }
    valid, errors = SchemaValidator.validate(invalid_data, schema)
    assert valid is False
    assert any("age" in e for e in errors)
    assert any("is_member" in e for e in errors)
    assert any("scores" in e for e in errors)


def test_verification_engine_schema_artifact():
    """Verify VerificationEngine handles schema artifact type with repair & validation."""
    schema = {
        "type": "object",
        "required": ["solution", "verified"],
        "properties": {
            "solution": {"type": "string"},
            "verified": {"type": "boolean"}
        }
    }

    # Pass case with single quotes and Python True needing auto-repair
    raw_str = "{'solution': 'x = 4', 'verified': True}"
    verif = VerificationEngine.verify_artifact("schema", {"raw": raw_str, "schema": schema})
    assert verif["verified"] is True
    assert verif["confidence"] >= 0.9
    assert verif["details"]["parsed"]["verified"] is True

    # Fail case with missing required field
    bad_raw = "{'other': 'val'}"
    verif_bad = VerificationEngine.verify_artifact("schema", {"raw": bad_raw, "schema": schema})
    assert verif_bad["verified"] is False
    assert "Missing required property" in verif_bad["reason"]
