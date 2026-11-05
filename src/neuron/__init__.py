"""
PROJECT: NEURON (Legacy Compatibility Stub for GliaCore 0.4.0)
The 'neuron' package has been rebranded to 'gliacore'.
Please update your imports to 'import gliacore'.
"""

import warnings
from typing import Any
import gliacore

warnings.warn(
    "The 'neuron' package namespace is deprecated and has been rebranded to 'gliacore'. "
    "Please update your imports to 'import gliacore'.",
    FutureWarning,
    stacklevel=2
)

__version__ = gliacore.__version__
__author__ = gliacore.__author__
__license__ = gliacore.__license__

__all__ = list(gliacore.__all__) + [
    "__version__",
    "__author__",
    "__license__",
    "Neuron",
    "NeuronEngine",
]


def __getattr__(name: str) -> Any:
    if name in ("Neuron", "NeuronEngine"):
        return getattr(gliacore, "NeuralCore")
    return getattr(gliacore, name)


def __dir__():
    return __all__
