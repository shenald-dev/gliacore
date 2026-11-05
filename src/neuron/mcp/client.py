"""
Legacy backward-compatibility stub for gliacore.mcp.client.
"""

from gliacore.mcp.client import GliaCoreMCPClient

# Compatibility alias
NeuronMCPClient = GliaCoreMCPClient

__all__ = ["GliaCoreMCPClient", "NeuronMCPClient"]
