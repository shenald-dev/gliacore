"""
Legacy backward-compatibility stub for gliacore.mcp.
"""

from gliacore.mcp import (
    MCPTool,
    JSONRPCRequest,
    JSONRPCResponse,
    LATEST_PROTOCOL_VERSION,
    GliaCoreMCPServer,
    GliaCoreMCPClient,
)
from neuron.mcp.server import NeuronMCPServer
from neuron.mcp.client import NeuronMCPClient

__all__ = [
    "MCPTool",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "LATEST_PROTOCOL_VERSION",
    "GliaCoreMCPServer",
    "GliaCoreMCPClient",
    "NeuronMCPServer",
    "NeuronMCPClient",
]
