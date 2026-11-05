"""
PROJECT: GLIACORE 0.4.0
An Edge-Optimized, Modular Micro-AI Collective Intelligence Ecosystem
"""

import importlib
from typing import Any

__version__ = "0.4.0"
__author__ = "Shenal Diluksha"
__license__ = "GPL-3.0-or-later"

_LAZY_EXPORTS = {
    "GliaCore": ("gliacore.core.engine", "GliaCore"),
    "NeuralCore": ("gliacore.core.engine", "NeuralCore"),
    "HardwareSupervisor": ("gliacore.core.hardware", "HardwareSupervisor"),
    "VRAMBudget": ("gliacore.core.hardware", "VRAMBudget"),
    "SynapseBus": ("gliacore.synapse.bus", "SynapseBus"),
    "SynapseMessage": ("gliacore.synapse.messages", "SynapseMessage"),
    "MessageType": ("gliacore.synapse.messages", "MessageType"),
    "GliaCoreMCPServer": ("gliacore.mcp.server", "GliaCoreMCPServer"),
    "GliaCoreMCPClient": ("gliacore.mcp.client", "GliaCoreMCPClient"),
    "JSONExtractor": ("gliacore.verification.schema", "JSONExtractor"),
    "SchemaValidator": ("gliacore.verification.schema", "SchemaValidator"),
    "ToolRegistry": ("gliacore.tools.registry", "ToolRegistry"),
    "ToolDefinition": ("gliacore.tools.registry", "ToolDefinition"),
    "SwarmConsensusEngine": ("gliacore.verification.swarm", "SwarmConsensusEngine"),
}

__all__ = [
    "GliaCore",
    "NeuralCore",
    "HardwareSupervisor",
    "VRAMBudget",
    "SynapseBus",
    "SynapseMessage",
    "MessageType",
    "GliaCoreMCPServer",
    "GliaCoreMCPClient",
    "JSONExtractor",
    "SchemaValidator",
    "ToolRegistry",
    "ToolDefinition",
    "SwarmConsensusEngine",
]


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        module_path, attr_name = _LAZY_EXPORTS[name]
        mod = importlib.import_module(module_path)
        val = getattr(mod, attr_name)
        globals()[name] = val
        return val
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    return __all__ + ["__version__", "__author__", "__license__"]
