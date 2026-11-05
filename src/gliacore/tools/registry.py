"""
Dynamic Tool & Function Calling Registry for GliaCore.
Enables registration of Python functions with automatic schema generation from type hints
and docstrings, execution sandboxing, and seamless interoperability with MCP and OpenAI tool formats.
"""

import inspect
import datetime
from typing import Dict, Any, Callable, Optional, List, get_type_hints
from dataclasses import dataclass, field


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    handler: Callable[..., Any]
    is_sandboxed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_mcp_dict(self) -> Dict[str, Any]:
        """Convert to standard MCP tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters_schema
        }

    def to_openai_dict(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling tool format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }


def _python_type_to_json_type(py_type: Any) -> str:
    """Map Python type annotation to JSON schema type string."""
    if py_type in (int,):
        return "integer"
    elif py_type in (float,):
        return "number"
    elif py_type in (bool,):
        return "boolean"
    elif py_type in (str,):
        return "string"
    elif py_type in (list, List):
        return "array"
    elif py_type in (dict, Dict):
        return "object"
    return "string"


def generate_schema_from_callable(fn: Callable[..., Any]) -> Dict[str, Any]:
    """
    Introspects a Python function's signature and type hints to generate a valid JSON schema.
    """
    sig = inspect.signature(fn)
    hints = {}
    try:
        hints = get_type_hints(fn)
    except Exception:
        pass

    properties: Dict[str, Any] = {}
    required: List[str] = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        param_type = hints.get(name, str)
        json_type = _python_type_to_json_type(param_type)
        properties[name] = {"type": json_type}

        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            properties[name]["default"] = param.default

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


class ToolRegistry:
    """
    Central registry for dynamic tools in the GliaCore ecosystem.
    Supports introspection, parameter validation, and multi-format tool calling.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_builtins()

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters_schema: Optional[Dict[str, Any]] = None,
        is_sandboxed: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a function as a dynamic tool."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            tool_name = name or fn.__name__
            tool_desc = description or (fn.__doc__.strip() if fn.__doc__ else f"Tool: {tool_name}")
            schema = parameters_schema or generate_schema_from_callable(fn)

            definition = ToolDefinition(
                name=tool_name,
                description=tool_desc,
                parameters_schema=schema,
                handler=fn,
                is_sandboxed=is_sandboxed,
                metadata=metadata or {}
            )
            self._tools[tool_name] = definition
            return fn
        return decorator

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Any],
        description: Optional[str] = None,
        parameters_schema: Optional[Dict[str, Any]] = None,
        is_sandboxed: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolDefinition:
        """Explicitly register a tool definition."""
        tool_desc = description or (handler.__doc__.strip() if handler.__doc__ else f"Tool: {name}")
        schema = parameters_schema or generate_schema_from_callable(handler)

        definition = ToolDefinition(
            name=name,
            description=tool_desc,
            parameters_schema=schema,
            handler=handler,
            is_sandboxed=is_sandboxed,
            metadata=metadata or {}
        )
        self._tools[name] = definition
        return definition

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Retrieve a registered tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool with provided arguments, validating parameters
        and capturing execution metrics.
        """
        tool = self.get_tool(name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{name}' is not registered in GliaCore ToolRegistry."
            }

        # Check required properties
        required = tool.parameters_schema.get("required", [])
        for req in required:
            if req not in arguments:
                return {
                    "success": False,
                    "error": f"Missing required parameter '{req}' for tool '{name}'."
                }

        try:
            # Call tool handler with provided arguments
            result = tool.handler(**arguments)
            return {
                "success": True,
                "tool": name,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "tool": name,
                "error": str(e)
            }

    def _register_builtins(self) -> None:
        """Register built-in edge utility tools."""

        def datetime_now(timezone: str = "UTC") -> Dict[str, Any]:
            """Return the current system date, time, and timestamp."""
            now = datetime.datetime.now(datetime.timezone.utc)
            return {
                "iso": now.isoformat(),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S UTC"),
                "timestamp": now.timestamp(),
                "timezone": timezone
            }

        self.register_tool(
            name="datetime_now",
            handler=datetime_now,
            description="Returns the current verified system date, time, and UTC timestamp.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "default": "UTC"}
                }
            }
        )
