"""
Base Neuron Abstraction for PROJECT: NEURON
Defines the lifecycle, contract, and communication hooks for all specialized neurons.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import torch
from neuron.synapse.bus import SynapseBus
from neuron.synapse.messages import SynapseMessage, MessageType


class BaseNeuron(ABC):
    """
    Abstract computational unit in the NEURON ecosystem.
    Each neuron operates independently, possesses a narrow specialization,
    communicates over the Synapse bus, and generates verifiable artifacts.
    """

    def __init__(self, neuron_id: str, name: str, specialization: str, bus: Optional[SynapseBus] = None, enable_gpu: bool = True):
        self.neuron_id = neuron_id
        self.name = name
        self.specialization = specialization
        self.bus = bus
        self.total_invocations = 0
        self.total_latency_ms = 0.0
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.device = torch.device("cuda:0" if self.enable_gpu else "cpu")

        if self.bus:
            self.bus.register_neuron(self.neuron_id)

    @abstractmethod
    def execute(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the specialized intelligence task.
        Must be implemented by each concrete Neuron.
        """
        pass

    def run(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrapper handling execution profiling, metrics, and Synapse dispatch.
        """
        start = time.perf_counter()
        self.total_invocations += 1

        try:
            # Simulate micro-adapter activation buffer on GPU when CUDA available
            if self.enable_gpu:
                act = torch.empty((25 * 1024 * 1024 // 4,), dtype=torch.float32, device=self.device)
                act.fill_(0.01)
                _ = torch.sum(act).item()
                del act

            result = self.execute(task_payload)
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.total_latency_ms += elapsed_ms

            response = {
                "success": True,
                "neuron_id": self.neuron_id,
                "specialization": self.specialization,
                "result": result,
                "latency_ms": round(elapsed_ms, 2),
                "error": None
            }

            # Emit intermediate artifact to Synapse bus if connected
            if self.bus:
                msg = SynapseMessage(
                    msg_type=MessageType.INTERMEDIATE_ARTIFACT,
                    sender_id=self.neuron_id,
                    recipient_id="neural_core",
                    topic=f"neuron.{self.specialization}",
                    payload=response
                )
                self.bus.publish(msg)

            return response
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            error_response = {
                "success": False,
                "neuron_id": self.neuron_id,
                "specialization": self.specialization,
                "result": None,
                "latency_ms": round(elapsed_ms, 2),
                "error": str(e)
            }
            return error_response

    def get_stats(self) -> Dict[str, Any]:
        """Return operational telemetry."""
        avg_latency = (self.total_latency_ms / self.total_invocations) if self.total_invocations > 0 else 0.0
        return {
            "neuron_id": self.neuron_id,
            "name": self.name,
            "specialization": self.specialization,
            "invocations": self.total_invocations,
            "avg_latency_ms": round(avg_latency, 2),
            "total_latency_ms": round(self.total_latency_ms, 2)
        }
