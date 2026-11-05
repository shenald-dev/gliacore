"""
Legacy backward-compatibility stub for gliacore.mcp.server.
"""

from gliacore.mcp.server import GliaCoreMCPServer

# Compatibility alias
NeuronMCPServer = GliaCoreMCPServer

__all__ = ["GliaCoreMCPServer", "NeuronMCPServer"]
