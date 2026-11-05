"""
Unit tests for Synapse Binary Message Serialization and Bus
"""

from gliacore.synapse.messages import SynapseMessage, MessageType
from gliacore.synapse.bus import SynapseBus


def test_synapse_message_serialization_roundtrip():
    original = SynapseMessage(
        msg_type=MessageType.INTERMEDIATE_ARTIFACT,
        sender_id="neuron_math_01",
        recipient_id="neural_core",
        topic="math.results",
        payload={"value": 42.0, "status": "exact"},
        confidence=0.99
    )

    packed_bytes = original.serialize()
    assert isinstance(packed_bytes, bytes)
    assert len(packed_bytes) > 0

    restored = SynapseMessage.deserialize(packed_bytes)
    assert restored.msg_id == original.msg_id
    assert restored.msg_type == MessageType.INTERMEDIATE_ARTIFACT
    assert restored.sender_id == "neuron_math_01"
    assert restored.recipient_id == "neural_core"
    assert restored.payload == {"value": 42.0, "status": "exact"}
    assert restored.confidence == 0.99


def test_synapse_bus_pub_sub():
    bus = SynapseBus()
    received_messages = []

    def on_math_event(msg: SynapseMessage):
        received_messages.append(msg)

    bus.subscribe("math.events", on_math_event)

    msg = SynapseMessage(
        msg_type=MessageType.TASK_DISPATCH,
        sender_id="neural_core",
        topic="math.events",
        payload={"formula": "x^2 + 5"}
    )

    bus.publish(msg)
    assert len(received_messages) == 1
    assert received_messages[0].payload["formula"] == "x^2 + 5"
    assert received_messages[0].latency_ms >= 0.0


def test_synapse_point_to_point_mailbox():
    bus = SynapseBus()
    bus.register_neuron("neuron_coder_01")

    msg = SynapseMessage(
        msg_type=MessageType.TASK_DISPATCH,
        sender_id="neural_core",
        recipient_id="neuron_coder_01",
        payload={"prompt": "def add(a, b): return a + b"}
    )

    bus.publish(msg)
    received = bus.receive("neuron_coder_01", timeout=0.1)
    assert received is not None
    assert received.recipient_id == "neuron_coder_01"
    assert received.payload["prompt"] == "def add(a, b): return a + b"
