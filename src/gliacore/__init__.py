"""
PROJECT: GLIACORE 0.4.0
An Edge-Optimized, Modular Micro-AI Collective Intelligence Ecosystem
"""

__version__ = "0.4.0"
__author__ = "Shenal Diluksha"
__license__ = "GPL-3.0-or-later"

from gliacore.core.engine import GliaCore, NeuralCore
from gliacore.core.hardware import HardwareSupervisor, VRAMBudget
from gliacore.synapse.bus import SynapseBus
from gliacore.synapse.messages import SynapseMessage, MessageType
from gliacore.mcp.server import GliaCoreMCPServer
from gliacore.mcp.client import GliaCoreMCPClient
from gliacore.verification.schema import JSONExtractor, SchemaValidator

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
]
