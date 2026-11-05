"""
Neuron Registry & Dynamic Discovery for PROJECT: NEURON
"""

from typing import Dict, List, Optional
from gliacore.neurons.base import BaseNeuron


class NeuronRegistry:
    """
    Central registry maintaining active neuron instances and their capability metadata.
    """

    def __init__(self):
        self._neurons: Dict[str, BaseNeuron] = {}
        self._specialization_map: Dict[str, List[str]] = {}

    def register(self, neuron: BaseNeuron) -> None:
        """Register a neuron instance into the ecosystem."""
        self._neurons[neuron.neuron_id] = neuron
        if neuron.specialization not in self._specialization_map:
            self._specialization_map[neuron.specialization] = []
        if neuron.neuron_id not in self._specialization_map[neuron.specialization]:
            self._specialization_map[neuron.specialization].append(neuron.neuron_id)

    def get_by_id(self, neuron_id: str) -> Optional[BaseNeuron]:
        """Lookup neuron by unique ID."""
        return self._neurons.get(neuron_id)

    def get_by_specialization(self, specialization: str) -> List[BaseNeuron]:
        """Lookup all neurons with a specific specialization."""
        ids = self._specialization_map.get(specialization, [])
        return [self._neurons[nid] for nid in ids if nid in self._neurons]

    def list_neurons(self) -> List[Dict[str, str]]:
        """List all registered neurons and their metadata."""
        return [
            {
                "neuron_id": n.neuron_id,
                "name": n.name,
                "specialization": n.specialization
            }
            for n in self._neurons.values()
        ]
