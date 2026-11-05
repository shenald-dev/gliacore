"""
Comprehensive Unit Tests for GliaCore Streaming Subsystem.
Tests event-driven stage generators, token streaming, and safety termination in streaming mode.
"""

from gliacore.core.engine import GliaCore


def test_streaming_event_sequence():
    """Verify process_stream yields stage transitions, tokens, and final completion event."""
    core = GliaCore(auto_load_model=False)
    try:
        events = list(core.process_stream("Calculate 25 * 4"))
        assert len(events) >= 3

        event_names = [e.get("event") for e in events]
        assert "stage" in event_names
        assert "done" in event_names

        # Check stage progression
        stages = [e.get("stage") for e in events if e.get("event") == "stage"]
        assert "Reflex Screening & Security" in stages
        assert "Adaptive Neural Routing" in stages

        # Check final completion payload
        done_event = [e for e in events if e.get("event") == "done"][0]
        assert done_event["status"] in ["SUCCESS", "VERIFIED", "UNVERIFIED"]
        assert "results" in done_event
        assert "task_id" in done_event
    finally:
        core.close()


def test_streaming_blocked_threat():
    """Verify process_stream halts immediately and emits BLOCKED event when threat detected."""
    core = GliaCore(auto_load_model=False)
    try:
        events = list(core.process_stream("rm -rf / --no-preserve-root"))
        done_events = [e for e in events if e.get("event") == "done"]
        assert len(done_events) == 1
        assert done_events[0]["status"] == "BLOCKED"
        assert "Blocked" in done_events[0]["response_markdown"]
    finally:
        core.close()


def test_model_runner_generate_stream():
    """Verify ModelRunner.generate_stream yields token chunks."""
    core = GliaCore(auto_load_model=False)
    try:
        tokens = list(core.model_runner.generate_stream("hello"))
        assert len(tokens) > 0
        joined = "".join(tokens)
        assert len(joined) > 20
        assert "GliaCore" in joined
    finally:
        core.close()
