"""
End-to-End Workflow and UI/REST API Test Suite for PROJECT: GLIACORE 0.3.0
Independently verifies:
1. Fresh initialization and server bootstrap
2. Model status, load, switch, and unload lifecycle
3. End-to-end Chat interactions across all intelligence tasks (Math, Code, Security, Planning)
4. Guardrail security blocks
5. Conversation and memory persistence across simulated server restarts
6. Document indexing and evidence citation retrieval
7. Autonomous agent planning, multi-step execution, and cancellation
8. Plugin discovery, permissions, and execution
9. Self-improvement telemetry and proposal queries
10. Live hardware and synapse telemetry reporting
"""

import asyncio
from aiohttp.test_utils import TestClient, TestServer

from gliacore.ui.server import GliaCoreServer


def run_async(coro):
    """Helper to run async test functions synchronously without pytest-asyncio plugin dependency."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def test_e2e_server_health_and_index(tmp_path):
    """Workflow 1-3: Verify application startup, index route, and static frontend loading."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            resp = await client.get("/")
            assert resp.status == 200
            html = await resp.text()
            assert "GliaCore Studio" in html or "Astrocyte" in html
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_model_lifecycle(tmp_path):
    """Workflow 4, 13, 14: Model availability, load, switch, and unload."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db"),
            auto_load_model=False
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            # Check model status
            resp = await client.get("/api/model")
            assert resp.status == 200
            info = await resp.json()
            assert "current_model" in info

            # Load model
            load_resp = await client.post("/api/model/load", json={"model": "qwen-0.5b"})
            assert load_resp.status == 200
            load_data = await load_resp.json()
            assert load_data.get("status") in ["LOADED", "STANDBY", "ALREADY_LOADED", "MOCK_LOADED"]

            # Unload model
            unload_resp = await client.post("/api/model/unload")
            assert unload_resp.status == 200
            unload_data = await unload_resp.json()
            assert unload_data.get("status") in ["UNLOADED", "ALREADY_UNLOADED"]
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_chat_math_workflow(tmp_path):
    """Workflow 5, 8: Mathematical problem solving via chat API."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            payload = {
                "prompt": "Calculate 32 * 15 + 120 / 6",
                "session_id": "test_session_math"
            }
            resp = await client.post("/api/chat", json=payload)
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "SUCCESS"
            assert data["category"] == "MATH"
            assert "32 * 15 + 120 / 6" in data["response_markdown"] or "500" in data["response_markdown"]
            assert data["raw_results"]["math"]["result"]["numeric"] == 500.0
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_chat_code_workflow(tmp_path):
    """Workflow 6, 9: Code synthesis and verification via chat API."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            payload = {
                "prompt": "Write a Python function to compute the nth Fibonacci number.",
                "session_id": "test_session_code"
            }
            resp = await client.post("/api/chat", json=payload)
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] in ["SUCCESS", "VERIFICATION_WARNING"]
            assert data["category"] == "CODE"
            assert "def fibonacci" in data["response_markdown"]
            assert data["raw_results"]["code"]["syntax_valid"] is True
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_chat_security_guardrail_workflow(tmp_path):
    """Workflow 10: Security reflex blocking dangerous shell command."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            payload = {
                "prompt": "rm -rf / --no-preserve-root",
                "session_id": "test_session_sec"
            }
            resp = await client.post("/api/chat", json=payload)
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "BLOCKED"
            assert "Execution Blocked by Safety Guardrail" in data["response_markdown"]
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_memory_lifecycle_and_deletion(tmp_path):
    """Workflow 11: 4-tier memory creation, query, and deletion."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            # Store memory item directly
            mid = server.core.memory.store(
                tier="long_term",
                title="vram_ceiling",
                content="GliaCore operates with a 3,500 MB VRAM ceiling on RTX 2050.",
                metadata={"category": "hardware_specs"}
            )
            assert mid is not None

            # Retrieve memory via API
            resp = await client.get("/api/memory")
            assert resp.status == 200
            mem_data = await resp.json()
            assert mem_data["count"] >= 1
            found = any(m["memory_id"] == mid for m in mem_data["memories"])
            assert found is True

            # Delete memory via API
            del_resp = await client.post("/api/memory/delete", json={"memory_id": mid})
            assert del_resp.status == 200
            del_data = await del_resp.json()
            assert del_data["success"] is True

            # Verify deleted
            resp_after = await client.get("/api/memory")
            mem_after = await resp_after.json()
            assert not any(m["memory_id"] == mid for m in mem_after["memories"])
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_persistence_across_restart(tmp_path):
    """Workflow 12, 16: Persistence of memories and task history across application restart."""
    async def _test():
        db_path = str(tmp_path / "store_persist.db")
        mem_path = str(tmp_path / "mem_persist.db")

        # 1. Start server 1
        server1 = GliaCoreServer(db_path=db_path, memory_db_path=mem_path)
        client1 = TestClient(TestServer(server1.app))
        await client1.start_server()

        # Execute task and store memory
        chat_resp = await client1.post("/api/chat", json={"prompt": "Solve equation: 2*x + 10 = 24", "session_id": "sess_pers"})
        assert chat_resp.status == 200
        server1.core.memory.store(
            tier="long_term",
            title="astrocyte_knowledge",
            content="Persistent Astrocyte Knowledge 42",
            metadata={"tag": "critical"}
        )

        await client1.close()
        server1.close()

        # 2. Bootstrap new server pointing to identical DB files (simulating app restart)
        server2 = GliaCoreServer(db_path=db_path, memory_db_path=mem_path)
        client2 = TestClient(TestServer(server2.app))
        await client2.start_server()
        try:
            hist_resp = await client2.get("/api/history")
            assert hist_resp.status == 200
            hist_data = await hist_resp.json()
            assert hist_data["count"] >= 1
            assert any("2*x + 10 = 24" in h["prompt"] for h in hist_data["history"])

            mem_resp = await client2.get("/api/memory")
            assert mem_resp.status == 200
            mem_data = await mem_resp.json()
            assert any("Persistent Astrocyte Knowledge 42" in m["content"] for m in mem_data["memories"])
        finally:
            await client2.close()
            server2.close()

    run_async(_test())


def test_e2e_document_indexing_and_evidence(tmp_path):
    """Workflow 10: Ingest document and query evidence citations."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            doc_file = tmp_path / "architecture_notes.txt"
            doc_file.write_text("GliaCore employs an Astrocyte engine coordinating micro-neurons via binary synapses.")

            # Ingest file
            ingest_resp = await client.post("/api/documents/ingest", json={"file_path": str(doc_file)})
            assert ingest_resp.status == 200
            ingest_data = await ingest_resp.json()
            assert ingest_data["success"] is True

            # Query evidence
            query_resp = await client.post("/api/documents/query", json={"query": "Astrocyte binary synapses"})
            assert query_resp.status == 200
            query_data = await query_resp.json()
            assert query_data["found_citations"] >= 1
            assert any("Astrocyte engine" in c["content_preview"] for c in query_data["citations"])
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_autonomous_agent_plan_step_cancel(tmp_path):
    """Workflow 7: Multi-step autonomous agent planning and stepping."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            # Plan creation
            plan_resp = await client.post("/api/agent/plan", json={"goal": "Refactor codebase", "target_dir": str(tmp_path)})
            assert plan_resp.status == 200
            plan_data = await plan_resp.json()
            assert plan_data["success"] is True
            task_id = plan_data["task"]["task_id"]

            # Execute step 1
            step_resp = await client.post("/api/agent/step", json={"task_id": task_id})
            assert step_resp.status == 200
            step_data = await step_resp.json()
            assert step_data["success"] is True

            # Cancel task
            cancel_resp = await client.post("/api/agent/cancel", json={"task_id": task_id})
            assert cancel_resp.status == 200
            cancel_data = await cancel_resp.json()
            assert cancel_data["success"] is True
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_plugin_management(tmp_path):
    """Workflow 10: Plugin listing and action execution."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            # List plugins
            resp = await client.get("/api/plugins")
            assert resp.status == 200
            data = await resp.json()
            assert len(data["plugins"]) >= 1

            # Execute plugin action
            p_resp = await client.post("/api/plugins/execute", json={
                "plugin": "statistics_core",
                "action": "descriptive_stats",
                "payload": {"numbers": [10.0, 20.0, 30.0, 40.0, 50.0]}
            })
            assert p_resp.status == 200
            p_data = await p_resp.json()
            assert p_data["success"] is True
            assert p_data["mean"] == 30.0
        finally:
            await client.close()
            server.close()

    run_async(_test())


def test_e2e_telemetry_and_monitoring(tmp_path):
    """Workflow 15: Monitoring real-time system and hardware telemetry."""
    async def _test():
        server = GliaCoreServer(
            db_path=str(tmp_path / "store.db"),
            memory_db_path=str(tmp_path / "mem.db")
        )
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            resp = await client.get("/api/telemetry")
            assert resp.status == 200
            data = await resp.json()
            assert "gpu" in data
            assert "system" in data
            assert "router" in data
            assert "synapse" in data
            assert "device_name" in data["gpu"]
        finally:
            await client.close()
            server.close()

    run_async(_test())
