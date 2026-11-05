"""
High-Performance Synapse Communication Bus for PROJECT: NEURON
Thread-safe, bounded, low-latency inter-neuron communication and routing.
"""

import time
import queue
import logging
import threading
from collections import defaultdict, deque
from typing import Dict, List, Callable, Optional, Any
from gliacore.synapse.messages import SynapseMessage


logger = logging.getLogger(__name__)


class SynapseBus:
    """
    Event-driven communication pathway connecting neurons.
    Facilitates binary serialized message dispatch with backpressure management,
    thread-safe topic pub/sub, and bounded history queues.
    """

    def __init__(self, max_queue_size: int = 1000, max_history_size: int = 1000):
        self.max_queue_size = max_queue_size
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Callable[[SynapseMessage], None]]] = defaultdict(list)
        self._neuron_mailboxes: Dict[str, queue.Queue] = {}
        self._history: deque = deque(maxlen=max_history_size)
        self._message_count: int = 0
        self._total_bytes_transferred: int = 0

    def register_neuron(self, neuron_id: str) -> None:
        """Create a dedicated FIFO mailbox for a neuron."""
        with self._lock:
            if neuron_id not in self._neuron_mailboxes:
                self._neuron_mailboxes[neuron_id] = queue.Queue(maxsize=self.max_queue_size)

    def subscribe(self, topic: str, callback: Callable[[SynapseMessage], None]) -> None:
        """Subscribe a callback to a specific topic."""
        with self._lock:
            self._subscribers[topic].append(callback)

    def publish(self, message: SynapseMessage) -> None:
        """
        Publish message over the synapse bus.
        Serializes and deserializes via msgpack to benchmark real binary pathway overhead.
        """
        start_time = time.perf_counter()

        # Binary serialization round-trip
        binary_payload = message.serialize()
        unpacked_msg = SynapseMessage.deserialize(binary_payload)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        unpacked_msg.latency_ms = round(elapsed_ms, 4)

        with self._lock:
            self._total_bytes_transferred += len(binary_payload)
            self._message_count += 1
            self._history.append(unpacked_msg)

            # 1. Point-to-point delivery
            if unpacked_msg.recipient_id in self._neuron_mailboxes:
                try:
                    self._neuron_mailboxes[unpacked_msg.recipient_id].put_nowait(unpacked_msg)
                except queue.Full:
                    # Backpressure: drop oldest item if queue is full
                    try:
                        self._neuron_mailboxes[unpacked_msg.recipient_id].get_nowait()
                        self._neuron_mailboxes[unpacked_msg.recipient_id].put_nowait(unpacked_msg)
                    except (queue.Empty, queue.Full):
                        pass

            # Snapshot callbacks to execute outside critical lock section
            topic_callbacks = list(self._subscribers.get(unpacked_msg.topic, []))
            wildcard_callbacks = list(self._subscribers.get("*", []))

        # 2. Topic-based pub/sub broadcast
        for callback in topic_callbacks:
            try:
                callback(unpacked_msg)
            except Exception as e:
                logger.debug("Synapse topic callback exception: %s", e)

        # 3. Wildcard listeners
        for callback in wildcard_callbacks:
            try:
                callback(unpacked_msg)
            except Exception as e:
                logger.debug("Synapse wildcard callback exception: %s", e)

    def receive(self, neuron_id: str, timeout: Optional[float] = 0.05) -> Optional[SynapseMessage]:
        """Receive the next message for a specific neuron from its mailbox."""
        mailbox = None
        with self._lock:
            mailbox = self._neuron_mailboxes.get(neuron_id)

        if not mailbox:
            return None
        try:
            return mailbox.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_telemetry(self) -> Dict[str, Any]:
        """Return bus throughput and communication telemetry."""
        with self._lock:
            return {
                "total_messages": self._message_count,
                "total_bytes_transferred": self._total_bytes_transferred,
                "active_mailboxes": len(self._neuron_mailboxes),
                "subscribed_topics": list(self._subscribers.keys()),
                "history_buffer_depth": len(self._history)
            }

    def clear(self) -> None:
        """Clear all message queues and history."""
        with self._lock:
            self._history.clear()
            for q in self._neuron_mailboxes.values():
                while not q.empty():
                    try:
                        q.get_nowait()
                    except queue.Empty:
                        break
