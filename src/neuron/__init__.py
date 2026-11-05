"""
PROJECT: NEURON
An Edge-Optimized, Modular Micro-AI Intelligence Ecosystem
"""

__version__ = "0.1.0"
__author__ = "Shenal Diluksha"
__license__ = "GPL-3.0-or-later"

from neuron.core.engine import NeuralCore
from neuron.core.hardware import HardwareSupervisor, VRAMBudget
from neuron.synapse.bus import SynapseBus
from neuron.synapse.messages import SynapseMessage, MessageType

__all__ = [
    "NeuralCore",
    "HardwareSupervisor",
    "VRAMBudget",
    "SynapseBus",
    "SynapseMessage",
    "MessageType",
]
