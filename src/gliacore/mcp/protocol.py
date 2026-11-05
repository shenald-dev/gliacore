"""
Model Context Protocol (MCP) & JSON-RPC 2.0 Protocol Specifications for GliaCore.
Implements the 2024-11-05 MCP specification for tool registration, invocation, and capabilities.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field

LATEST_PROTOCOL_VERSION = "2024-11-05"
SUPPORTED_PROTOCOL_VERSIONS = ["2024-11-05", "0.1.0"]

# JSON-RPC 2.0 Error Codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class JSONRPCResponse:
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            d["error"] = self.error
        else:
            d["result"] = self.result
        return d


@dataclass
class JSONRPCRequest:
    method: str
    id: Optional[Any] = None
    params: Dict[str, Any] = field(default_factory=dict)
    jsonrpc: str = "2.0"
