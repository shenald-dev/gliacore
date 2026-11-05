"""
Legacy backward-compatibility stub for gliacore.mcp.protocol.
"""

from gliacore.mcp.protocol import (
    MCPTool,
    JSONRPCRequest,
    JSONRPCResponse,
    LATEST_PROTOCOL_VERSION,
    PARSE_ERROR,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

__all__ = [
    "MCPTool",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "LATEST_PROTOCOL_VERSION",
    "PARSE_ERROR",
    "INVALID_REQUEST",
    "METHOD_NOT_FOUND",
    "INVALID_PARAMS",
    "INTERNAL_ERROR",
]
