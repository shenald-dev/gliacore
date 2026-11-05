"""
Schema-Constrained Decoding and JSON Auto-Repair Engine for GliaCore.
Provides robust JSON extraction, syntactic self-repair (handling malformed markdown,
trailing commas, single quotes, Python-style booleans/None), and schema validation.
"""

import re
import json
from typing import Dict, Any, Tuple, Optional, List


class JSONExtractor:
    """
    Extracts and repairs JSON payloads from raw LLM or neuron output,
    recovering from formatting errors, code fences, and conversational preamble.
    """

    @staticmethod
    def extract_json_candidate(text: str) -> str:
        """
        Extract the best candidate JSON string from text containing markdown fences or commentary.
        """
        if not text:
            return ""

        # 1. Look for explicit ```json ... ``` or ``` ... ``` code blocks
        fence_match = re.search(r"```(?:json)?\s*([\{\[].*?[\}\]])\s*```", text, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()

        # 2. Look for outermost balanced { ... } or [ ... ]
        first_curly = text.find("{")
        last_curly = text.rfind("}")
        first_bracket = text.find("[")
        last_bracket = text.rfind("]")

        candidates = []
        if first_curly != -1 and last_curly != -1 and last_curly > first_curly:
            candidates.append((first_curly, last_curly, text[first_curly:last_curly + 1]))

        if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
            candidates.append((first_bracket, last_bracket, text[first_bracket:last_bracket + 1]))

        if candidates:
            # Pick the candidate that spans the largest portion of text
            candidates.sort(key=lambda c: len(c[2]), reverse=True)
            return candidates[0][2].strip()

        return text.strip()

    @staticmethod
    def repair_json_string(raw: str) -> str:
        """
        Syntactically repairs common LLM JSON syntax mistakes:
        - Trailing commas in objects and arrays
        - Python-style booleans and None (True -> true, False -> false, None -> null)
        - Single-quoted keys and strings -> double quotes
        - Unquoted object keys
        """
        if not raw:
            return "{}"

        s = raw.strip()

        # Replace Python constants with JSON constants
        s = re.sub(r"\bTrue\b", "true", s)
        s = re.sub(r"\bFalse\b", "false", s)
        s = re.sub(r"\bNone\b", "null", s)

        # Replace single-quoted property keys: {'key': -> {"key":
        s = re.sub(r"([{,]\s*)'([a-zA-Z0-9_\-\.]+)'\s*:", r'\1"\2":', s)

        # Replace single-quoted string values: : 'value' -> : "value"
        s = re.sub(r":\s*'([^']*)'", r': "\1"', s)

        # Replace single-quoted array elements: ['a', 'b']
        s = re.sub(r"\[\s*'([^']*)'", r'["\1"', s)
        s = re.sub(r",\s*'([^']*)'", r', "\1"', s)

        # Remove trailing commas before closing braces/brackets
        s = re.sub(r",\s*\}", "}", s)
        s = re.sub(r",\s*\]", "]", s)

        # Unquoted keys: { key: "val" } -> { "key": "val" }
        s = re.sub(r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', s)

        return s

    @classmethod
    def parse_and_repair(cls, raw_text: str) -> Tuple[bool, Optional[Any], str]:
        """
        Attempt standard json.loads. If it fails, extract candidate, apply repairs,
        and try again. Returns (success, parsed_obj_or_none, message).
        """
        # Try direct parse
        try:
            parsed = json.loads(raw_text)
            return True, parsed, "Parsed directly without repair"
        except Exception:
            pass

        # Extract candidate
        candidate = cls.extract_json_candidate(raw_text)
        try:
            parsed = json.loads(candidate)
            return True, parsed, "Parsed from candidate extraction"
        except Exception:
            pass

        # Apply syntactic repairs
        repaired = cls.repair_json_string(candidate)
        try:
            parsed = json.loads(repaired)
            return True, parsed, "Parsed after heuristic syntax repair"
        except Exception as e:
            return False, None, f"Failed to parse JSON even after repair: {e}"


class SchemaValidator:
    """
    Validates JSON data structures against a schema specification (type, required keys).
    Supports lightweight validation without requiring external heavy dependencies.
    """

    @staticmethod
    def validate(data: Any, schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates data against a lightweight JSON schema definition.
        Supported types: 'object', 'array', 'string', 'number', 'integer', 'boolean'.
        """
        errors: List[str] = []
        expected_type = schema.get("type")

        if expected_type == "object":
            if not isinstance(data, dict):
                return False, [f"Expected object (dict), got {type(data).__name__}"]

            # Check required fields
            required = schema.get("required", [])
            for req in required:
                if req not in data:
                    errors.append(f"Missing required property: '{req}'")

            # Check property types if defined
            properties = schema.get("properties", {})
            for key, prop_schema in properties.items():
                if key in data:
                    val = data[key]
                    val_type = prop_schema.get("type")
                    if val_type == "string" and not isinstance(val, str):
                        errors.append(f"Property '{key}' must be string, got {type(val).__name__}")
                    elif val_type == "integer" and not (isinstance(val, int) and not isinstance(val, bool)):
                        errors.append(f"Property '{key}' must be integer, got {type(val).__name__}")
                    elif val_type == "number" and not (isinstance(val, (int, float)) and not isinstance(val, bool)):
                        errors.append(f"Property '{key}' must be number, got {type(val).__name__}")
                    elif val_type == "boolean" and not isinstance(val, bool):
                        errors.append(f"Property '{key}' must be boolean, got {type(val).__name__}")
                    elif val_type == "array" and not isinstance(val, list):
                        errors.append(f"Property '{key}' must be array, got {type(val).__name__}")
                    elif val_type == "object" and not isinstance(val, dict):
                        errors.append(f"Property '{key}' must be object, got {type(val).__name__}")

        elif expected_type == "array":
            if not isinstance(data, list):
                return False, [f"Expected array (list), got {type(data).__name__}"]
            items_schema = schema.get("items")
            if items_schema:
                for idx, item in enumerate(data):
                    ok, item_errs = SchemaValidator.validate(item, items_schema)
                    if not ok:
                        errors.extend([f"Item [{idx}]: {e}" for e in item_errs])

        return len(errors) == 0, errors
