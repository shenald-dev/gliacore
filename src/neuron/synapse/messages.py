"""
Binary Message Protocols for NEURON Synapses
Using MessagePack for zero-overhead serialization.
"""

import time
import uuid
import msgpack
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass, field, asdict


class MessageType(str, Enum):
    TASK_DISPATCH = "task_dispatch"
    INTERMEDIATE_ARTIFACT = "intermediate_artifact"
    VERIFICATION_REQUEST = "verification_request"
    VERIFICATION_RESULT = "verification_result"
    FEEDBACK_SIGNAL = "feedback_signal"
    RESULT_SYNTHESIS = "result_synthesis"
    HEARTBEAT = "heartbeat"


@dataclass
class SynapseMessage:
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    msg_type: MessageType = MessageType.TASK_DISPATCH
    sender_id: str = "neural_core"
    recipient_id: str = "broadcast"
    topic: str = "general"
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    latency_ms: float = 0.0

    def serialize(self) -> bytes:
        """Pack message into high-speed MessagePack binary bytes."""
        data = asdict(self)
        data["msg_type"] = self.msg_type.value
        return msgpack.packb(data, use_bin_type=True)

    @classmethod
    def deserialize(cls, raw_bytes: bytes) -> "SynapseMessage":
        """Unpack message from binary MessagePack bytes."""
        data = msgpack.unpackb(raw_bytes, raw=False)
        data["msg_type"] = MessageType(data["msg_type"])
        return cls(**data)
