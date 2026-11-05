"""
PROJECT: NEURON (Legacy Compatibility Stub for GliaCore 0.4.0)
The 'neuron' package has been rebranded to 'gliacore'.
Please update your imports to 'import gliacore'.
"""

import warnings
from gliacore import (
    GliaCore,
    NeuralCore,
    HardwareSupervisor,
    VRAMBudget,
    SynapseBus,
    SynapseMessage,
    MessageType,
    GliaCoreMCPServer,
    GliaCoreMCPClient,
    JSONExtractor,
    SchemaValidator,
    ToolRegistry,
    SwarmConsensusEngine,
    __version__,
    __author__,
    __license__,
)

warnings.warn(
    "The 'neuron' package namespace is deprecated and has been rebranded to 'gliacore'. "
    "Please update your imports to 'import gliacore'.",
    FutureWarning,
    stacklevel=2
)

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
    "SwarmConsensusEngine",
    "__version__",
    "__author__",
    "__license__",
]
