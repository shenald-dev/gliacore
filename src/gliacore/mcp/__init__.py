"""
GliaCore Model Context Protocol (MCP) Subsystem.
Provides full MCP 2024-11-05 client and server implementations for GliaCore.
"""

from gliacore.mcp.protocol import (
    MCPTool,
    JSONRPCRequest,
    JSONRPCResponse,
    LATEST_PROTOCOL_VERSION,
)
from gliacore.mcp.server import GliaCoreMCPServer
from gliacore.mcp.client import GliaCoreMCPClient

__all__ = [
    "MCPTool",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "LATEST_PROTOCOL_VERSION",
    "GliaCoreMCPServer",
    "GliaCoreMCPClient",
]
