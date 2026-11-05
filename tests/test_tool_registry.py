"""
Unit tests for GliaCore Dynamic Tool Registry and Function Calling Subsystem.
Tests decorator-based registration, automatic JSON schema generation from Python type hints,
parameter validation, and execution sandboxing.
"""

from gliacore.tools.registry import ToolRegistry, generate_schema_from_callable
from gliacore.core.engine import GliaCore
from neuron.tools.registry import ToolRegistry as LegacyToolRegistry


def test_schema_generation_from_callable():
    """Verify automatic generation of valid JSON schema from Python type hints."""
    def sample_func(query: str, count: int, threshold: float = 0.5, flag: bool = True) -> dict:
        """Sample function for testing schema generation."""
        return {}

    schema = generate_schema_from_callable(sample_func)
    assert schema["type"] == "object"
    props = schema["properties"]
    assert props["query"]["type"] == "string"
    assert props["count"]["type"] == "integer"
    assert props["threshold"]["type"] == "number"
    assert props["threshold"]["default"] == 0.5
    assert props["flag"]["type"] == "boolean"
    assert "query" in schema["required"]
    assert "count" in schema["required"]
    assert "threshold" not in schema["required"]


def test_tool_registry_registration_and_execution():
    """Verify registering a custom function via decorator and executing it."""
    registry = ToolRegistry()

    @registry.register(name="add_numbers", description="Add two integers")
    def add(a: int, b: int) -> int:
        return a + b

    tool = registry.get_tool("add_numbers")
    assert tool is not None
    assert tool.name == "add_numbers"
    assert tool.description == "Add two integers"

    # Execute with valid arguments
    res = registry.execute_tool("add_numbers", {"a": 10, "b": 32})
    assert res["success"] is True
    assert res["result"] == 42

    # Execute with missing argument
    err_res = registry.execute_tool("add_numbers", {"a": 10})
    assert err_res["success"] is False
    assert "Missing required parameter" in err_res["error"]


def test_tool_registry_builtin_tools():
    """Verify default built-in tools (datetime_now) are registered."""
    registry = ToolRegistry()
    tool = registry.get_tool("datetime_now")
    assert tool is not None

    res = registry.execute_tool("datetime_now", {})
    assert res["success"] is True
    assert "iso" in res["result"]
    assert "timestamp" in res["result"]


def test_gliacore_engine_tool_integration():
    """Verify GliaCore engine exposes dynamic tools through list_tools and execute_tool."""
    core = GliaCore(auto_load_model=False)
    try:
        tools = core.list_tools()
        assert len(tools) >= 4
        tool_names = [t["name"] for t in tools]
        assert "math_solve" in tool_names
        assert "code_run" in tool_names
        assert "memory_query" in tool_names
        assert "datetime_now" in tool_names

        # Execute math tool
        res = core.execute_tool("math_solve", {"expression": "Calculate 40 * 25"})
        assert res["success"] is True
        assert res["result"]["numeric"] == 1000.0
    finally:
        core.close()


def test_legacy_neuron_tool_registry_compatibility():
    """Verify backward compatibility of neuron.tools.registry."""
    registry = LegacyToolRegistry()
    assert registry.get_tool("datetime_now") is not None
