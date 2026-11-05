"""
PROJECT: GLIACORE 0.3.0
An Edge-Optimized, Modular Micro-AI Collective Intelligence Ecosystem
"""

__version__ = "0.3.0"
__author__ = "Shenal Diluksha"
__license__ = "GPL-3.0-or-later"

from gliacore.core.engine import GliaCore, NeuralCore
from gliacore.core.hardware import HardwareSupervisor, VRAMBudget
from gliacore.synapse.bus import SynapseBus
from gliacore.synapse.messages import SynapseMessage, MessageType

__all__ = [
    "GliaCore",
    "NeuralCore",
    "HardwareSupervisor",
    "VRAMBudget",
    "SynapseBus",
    "SynapseMessage",
    "MessageType",
]
