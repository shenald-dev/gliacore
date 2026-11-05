"""
Local Web Server & REST API for PROJECT: GLIACORE 0.4.0
Provides async endpoints for the Interactive Chat UI, live neural activity telemetry,
system monitoring, 4-tier memory explorer, autonomous agent execution, and plugin management.
"""

import os
import json
import asyncio
import threading
from pathlib import Path

from aiohttp import web

from gliacore.core.engine import GliaCore
from gliacore.mcp.server import GliaCoreMCPServer
from gliacore.verification.schema import JSONExtractor, SchemaValidator

STATIC_DIR = Path(__file__).parent / "static"


# Backward-compatibility alias
NeuronServer = None

class GliaCoreServer:
    def __init__(self, db_path=None, memory_db_path=None, auto_load_model: bool = True):
        self.core = GliaCore(db_path=db_path, memory_db_path=memory_db_path)
        self.mcp_server = GliaCoreMCPServer(core=self.core)
        self.app = web.Application()
        self._setup_routes()

        if auto_load_model and os.environ.get("GLIACORE_NO_AUTOLOAD") != "1" and os.environ.get("NEURON_NO_AUTOLOAD") != "1":
            try:
                res = self.core.model_runner.load_model("qwen-0.5b")
                if res.get("is_real_weights"):
                    print(f"[*] Local SLM active on {self.core.model_runner.device}: {self.core.model_runner.SUPPORTED_MODELS['qwen-0.5b']['name']}")
            except Exception as e:
                print(f"[*] Standby mode: {e}")

    def _setup_routes(self) -> None:
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_post("/api/chat", self.handle_chat)
        self.app.router.add_post("/api/chat/stream", self.handle_chat_stream)
        self.app.router.add_get("/api/telemetry", self.handle_telemetry)
        self.app.router.add_get("/api/neurons", self.handle_neurons)
        self.app.router.add_get("/api/model", self.handle_model_info)
        self.app.router.add_post("/api/model/load", self.handle_model_load)
        self.app.router.add_post("/api/model/unload", self.handle_model_unload)
        self.app.router.add_get("/api/history", self.handle_history)

        # MCP and Schema Endpoints
        self.app.router.add_post("/api/mcp", self.handle_mcp_jsonrpc)
        self.app.router.add_get("/api/mcp/tools", self.handle_mcp_tools)
        self.app.router.add_post("/api/schema/validate", self.handle_schema_validate)
        self.app.router.add_post("/api/schema/repair", self.handle_schema_repair)

        # Phase 3 Advanced Capability Endpoints
        self.app.router.add_get("/api/memory", self.handle_memory_list)
        self.app.router.add_post("/api/memory/delete", self.handle_memory_delete)
        self.app.router.add_post("/api/documents/ingest", self.handle_doc_ingest)
        self.app.router.add_post("/api/documents/query", self.handle_doc_query)
        self.app.router.add_post("/api/agent/plan", self.handle_agent_plan)
        self.app.router.add_post("/api/agent/step", self.handle_agent_step)
        self.app.router.add_post("/api/agent/cancel", self.handle_agent_cancel)
        self.app.router.add_get("/api/plugins", self.handle_plugins_list)
        self.app.router.add_post("/api/plugins/execute", self.handle_plugin_execute)
        self.app.router.add_get("/api/improvement", self.handle_improvement_insights)

        self.app.router.add_static("/static", str(STATIC_DIR), name="static")

    async def handle_index(self, request: web.Request) -> web.Response:
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            return web.Response(text="GliaCore Studio frontend not yet generated.", status=404)
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        return web.Response(text=content, content_type="text/html")

    async def handle_chat(self, request: web.Request) -> web.Response:
        """Execute task through NeuralCore."""
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON body"}, status=400)

        prompt = body.get("prompt", "").strip()
        if not prompt:
            return web.json_response({"error": "Prompt cannot be empty"}, status=400)

        session_id = body.get("session_id", "default")

        # Run NeuralCore processing in thread pool to avoid blocking async event loop
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, self.core.process, prompt, None, session_id)

        # Synthesize user-facing response message from results
        synthesized_text = ""
        if res["status"] == "BLOCKED":
            synthesized_text = f"**Execution Blocked by Safety Guardrail**\n\nReason: {res.get('reason')}"
        else:
            parts = []
            results = res.get("results", {})
            if "math" in results:
                m = results["math"]
                parts.append("### Mathematical Verification (SymPy)\n")
                if m.get("operation") == "evaluate":
                    parts.append(f"- **Expression:** `{m.get('expression', m.get('extracted_expression'))}`")
                    res_val = m.get("result", {}).get("numeric", m.get("result", {}).get("exact"))
                    parts.append(f"- **Exact Result:** **{res_val}**")
                elif m.get("operation") == "solve":
                    parts.append(f"- **Equation:** `{m.get('equation', m.get('extracted_equation'))}`")
                    parts.append(f"- **Solutions:** `{m.get('result', {}).get('solutions')}`")

            if "code" in results:
                c = results["code"]
                parts.append("\n### Code Synthesis & Verification (AST + Sandbox)\n")
                code_snippet = c.get("synthesized_code") or c.get("analyzed_code") or ""
                parts.append(f"```python\n{code_snippet}\n```")
                parts.append(f"- **Syntax Valid:** `{c.get('syntax_valid')}`")
                if c.get("execution"):
                    exec_info = c["execution"]
                    if exec_info.get("stdout"):
                        parts.append(f"- **Runtime Output:**\n```\n{exec_info['stdout']}\n```")
                    if exec_info.get("error"):
                        parts.append(f"- **Runtime Error:** `{exec_info['error']}`")

            if "reasoning" in results:
                r = results["reasoning"]
                parts.append(f"\n{r.get('text', r.get('analysis', ''))}")

            # Note reflection repairs if any occurred
            if res.get("reflection_repairs"):
                repairs = res["reflection_repairs"]
                parts.append(f"\n> *[Cognitive Self-Repair]: {len(repairs)} syntax/runtime error(s) automatically corrected during reflection loop.*")

            synthesized_text = "\n".join(parts) if parts else "Task processed successfully."

        response_payload = {
            "task_id": res["task_id"],
            "session_id": session_id,
            "status": res["status"],
            "category": res.get("category"),
            "difficulty": res.get("difficulty"),
            "consensus_score": res.get("consensus_score", 1.0),
            "total_latency_ms": res.get("total_latency_ms", 0.0),
            "response_markdown": synthesized_text,
            "raw_results": res.get("results", {}),
            "reflection_repairs": res.get("reflection_repairs", []),
            "execution_timeline": res.get("execution_timeline", []),
            "hardware_telemetry": res.get("hardware_telemetry", {}),
            "synapse_telemetry": res.get("synapse_telemetry", {})
        }
        return web.json_response(response_payload)

    async def handle_telemetry(self, request: web.Request) -> web.Response:
        """Returns real-time system, router, and GPU metrics."""
        telem = self.core.get_system_telemetry()
        return web.json_response(telem)

    async def handle_neurons(self, request: web.Request) -> web.Response:
        """Returns list of registered neurons and their statistics."""
        neurons = []
        for n in self.core.registry._neurons.values():
            neurons.append(n.get_stats())
        return web.json_response({"neurons": neurons, "total_count": len(neurons)})

    async def handle_model_info(self, request: web.Request) -> web.Response:
        """Returns active model runner configuration."""
        info = self.core.model_runner.get_info()
        return web.json_response(info)

    async def handle_model_load(self, request: web.Request) -> web.Response:
        """Load a foundation model into memory."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        model_key = body.get("model", "qwen-0.5b")
        force_cpu = body.get("force_cpu", False)
        
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, self.core.model_runner.load_model, model_key, force_cpu)
        return web.json_response(res)

    async def handle_model_unload(self, request: web.Request) -> web.Response:
        """Unload active foundation model and purge VRAM."""
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, self.core.model_runner.unload_model)
        return web.json_response(res)

    async def handle_history(self, request: web.Request) -> web.Response:
        """Fetch past task history."""
        cursor = self.core.storage.conn.execute(
            "SELECT task_id, prompt, category, verification_status, latency_ms, created_at FROM task_history ORDER BY created_at DESC LIMIT 50"
        )
        rows = [
            {
                "task_id": r[0],
                "prompt": r[1],
                "category": r[2],
                "status": r[3],
                "latency_ms": r[4],
                "created_at": r[5]
            }
            for r in cursor.fetchall()
        ]
        return web.json_response({"history": rows, "count": len(rows)})

    # =========================================================================
    # Phase 3 Capability Handlers
    # =========================================================================
    async def handle_memory_list(self, request: web.Request) -> web.Response:
        """List 4-tier memory items."""
        tier = request.query.get("tier")
        memories = self.core.memory.list_all(tier=tier, limit=50)
        return web.json_response({"memories": memories, "count": len(memories)})

    async def handle_memory_delete(self, request: web.Request) -> web.Response:
        """Delete a memory item."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        mid = body.get("memory_id")
        if not mid:
            return web.json_response({"error": "memory_id is required"}, status=400)
        deleted = self.core.memory.delete(mid)
        return web.json_response({"success": deleted})

    async def handle_doc_ingest(self, request: web.Request) -> web.Response:
        """Ingest a local document into knowledge storage."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        file_path = body.get("file_path")
        if not file_path:
            return web.json_response({"error": "file_path is required"}, status=400)
        res = self.core.document_indexer.ingest_file(file_path)
        return web.json_response(res)

    async def handle_doc_query(self, request: web.Request) -> web.Response:
        """Search evidence citations in ingested documents."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        q = body.get("query", "")
        res = self.core.document_indexer.query_evidence(q)
        return web.json_response(res)

    async def handle_agent_plan(self, request: web.Request) -> web.Response:
        """Create a multi-step autonomous agent plan."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        goal = body.get("goal", "Analyze repository")
        target_dir = body.get("target_dir", ".")
        task = self.core.agent.create_plan(goal, target_dir)
        from dataclasses import asdict
        return web.json_response({"success": True, "task": asdict(task)})

    async def handle_agent_step(self, request: web.Request) -> web.Response:
        """Execute next step of an autonomous agent task."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        task_id = body.get("task_id")
        res = self.core.agent.execute_step(task_id)
        return web.json_response(res)

    async def handle_agent_cancel(self, request: web.Request) -> web.Response:
        """Cancel autonomous agent task."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        task_id = body.get("task_id")
        cancelled = self.core.agent.cancel_task(task_id)
        return web.json_response({"success": cancelled})

    async def handle_plugins_list(self, request: web.Request) -> web.Response:
        """List registered plugins."""
        plugins = self.core.plugin_manager.list_plugins()
        return web.json_response({"plugins": plugins})

    async def handle_plugin_execute(self, request: web.Request) -> web.Response:
        """Execute action via a registered plugin."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        plugin_name = body.get("plugin")
        action = body.get("action")
        payload = body.get("payload", {})
        res = self.core.plugin_manager.execute_plugin(plugin_name, action, payload)
        return web.json_response(res)

    async def handle_improvement_insights(self, request: web.Request) -> web.Response:
        """Get self-improvement telemetry and proposals."""
        insights = self.core.self_improvement.get_insights()
        return web.json_response(insights)


    async def handle_chat_stream(self, request: web.Request) -> web.StreamResponse:
        """Stream token generation and pipeline stages using Server-Sent Events (SSE)."""
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON body"}, status=400)

        prompt = body.get("prompt", "").strip()
        if not prompt:
            return web.json_response({"error": "Prompt cannot be empty"}, status=400)

        session_id = body.get("session_id", "default")

        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        await response.prepare(request)

        loop = asyncio.get_running_loop()
        event_queue = asyncio.Queue()

        def stream_worker():
            try:
                for event in self.core.process_stream(prompt, session_id=session_id):
                    loop.call_soon_threadsafe(event_queue.put_nowait, event)
            except Exception as ex:
                loop.call_soon_threadsafe(event_queue.put_nowait, {"event": "error", "error": str(ex)})
            finally:
                loop.call_soon_threadsafe(event_queue.put_nowait, None)

        worker_th = threading.Thread(target=stream_worker, daemon=True)
        worker_th.start()

        while True:
            event = await event_queue.get()
            if event is None:
                break
            event_type = event.get("event", "message")
            payload = json.dumps(event)
            await response.write(f"event: {event_type}\ndata: {payload}\n\n".encode("utf-8"))

        return response

    async def handle_mcp_jsonrpc(self, request: web.Request) -> web.Response:
        """Standard MCP JSON-RPC 2.0 endpoint."""
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}, status=400)

        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None, self.mcp_server.handle_request, body)
        if res is None:
            return web.Response(status=204)
        return web.json_response(res)

    async def handle_mcp_tools(self, request: web.Request) -> web.Response:
        """List registered MCP tools."""
        tools = [tool.to_dict() for tool in self.mcp_server._tools.values()]
        return web.json_response({"tools": tools, "count": len(tools)})

    async def handle_tools_list(self, request: web.Request) -> web.Response:
        """List registered dynamic tools."""
        tools = self.core.list_tools()
        return web.json_response({"tools": tools, "count": len(tools)})

    async def handle_tool_execute(self, request: web.Request) -> web.Response:
        """Execute a tool dynamically via ToolRegistry."""
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        tool_name = body.get("name")
        args = body.get("arguments", {})
        if not tool_name:
            return web.json_response({"error": "Tool name is required"}, status=400)
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None, self.core.execute_tool, tool_name, args)
        return web.json_response(res)

    async def handle_schema_validate(self, request: web.Request) -> web.Response:
        """Validate JSON data against a provided schema."""
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        data = body.get("data")
        schema = body.get("schema", {})
        valid, errors = SchemaValidator.validate(data, schema)
        return web.json_response({"valid": valid, "errors": errors})

    async def handle_schema_repair(self, request: web.Request) -> web.Response:
        """Parse and repair malformed JSON strings."""
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        raw_text = body.get("text", "")
        success, parsed, message = JSONExtractor.parse_and_repair(raw_text)
        return web.json_response({"success": success, "parsed": parsed, "message": message})

    def close(self) -> None:
        self.core.close()
        self.mcp_server.close()


def create_app() -> web.Application:
    server = GliaCoreServer()
    return server.app


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = GliaCoreServer()
    print("=" * 70)
    print("PROJECT: GLIACORE 0.4.0 — ADVANCED MODULAR MICRO-AI COLLECTIVE INTELLIGENCE ECOSYSTEM")
    print("Target Hardware: NVIDIA RTX 2050 (4 GB VRAM) | 16 GB System RAM")
    print(f"Server URL: http://{host}:{port}")
    print("Press Ctrl+C to terminate.")
    print("=" * 70)
    try:
        web.run_app(server.app, host=host, port=port, print=None)
    finally:
        server.close()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="GliaCore 0.4.0 — Edge Micro-AI Collective Intelligence Ecosystem")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the GliaCore Studio web server and API")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")

    # MCP command
    subparsers.add_parser("mcp", help="Run Model Context Protocol (MCP) server over stdio for Claude Desktop / Cursor")

    # Version command
    subparsers.add_parser("version", help="Print GliaCore version")

    # Tools command
    subparsers.add_parser("tools", help="List all registered dynamic tools in the ecosystem")

    # Telemetry command
    subparsers.add_parser("telemetry", help="Display real-time hardware, VRAM, and neuron metrics")

    # One-shot Chat command
    chat_parser = subparsers.add_parser("chat", help="Execute a prompt through GliaCore from terminal")
    chat_parser.add_argument("prompt", help="Prompt or task to execute")

    # Interactive Console command
    subparsers.add_parser("console", help="Launch interactive command-line session")

    args, _ = parser.parse_known_args()

    if args.command == "mcp":
        server = GliaCoreMCPServer()
        try:
            server.run_stdio()
        finally:
            server.close()
    elif args.command == "version":
        from gliacore import __version__
        print(f"GliaCore v{__version__}")
    elif args.command == "tools":
        core = GliaCore(auto_load_model=False)
        tools = core.list_tools()
        print(f"\nRegistered GliaCore Tools ({len(tools)} total):")
        print("-" * 65)
        for t in tools:
            print(f"  * {t['name']:<22} | {t.get('description', '')[:40]}")
        print("-" * 65)
        core.close()
    elif args.command == "telemetry":
        core = GliaCore(auto_load_model=False)
        telem = core.get_system_telemetry()
        gpu = telem.get("gpu", {})
        sys_ram = telem.get("system", {})
        print("\n--- GliaCore Hardware Telemetry ---")
        print(f"GPU Device:       {gpu.get('device_name', 'None')}")
        print(f"CUDA Available:   {gpu.get('cuda_available')}")
        print(f"VRAM Allocated:   {gpu.get('allocated_vram_mb', 0)} MB / {gpu.get('total_vram_mb', 0)} MB")
        print(f"Host Free RAM:    {sys_ram.get('free_ram_mb', 0)} MB")
        print(f"Task Latencies:   {telem.get('tasks', {}).get('avg_latency_ms', 0)} ms avg")
        core.close()
    elif args.command == "chat":
        core = GliaCore(auto_load_model=False)
        res = core.process(args.prompt)
        print(f"\n[Status: {res['status']}] (Latency: {res['total_latency_ms']} ms)")
        print("-" * 60)
        results = res.get("results", {})
        if "math" in results:
            print(f"Math Result: {results['math'].get('result')}")
        elif "code" in results:
            print(f"Code Output:\n{results['code'].get('synthesized_code')}")
        elif "reasoning" in results:
            print(results["reasoning"].get("text", ""))
        else:
            print(res.get("output", "Processed."))
        core.close()
    elif args.command == "console":
        core = GliaCore(auto_load_model=False)
        print("GliaCore Interactive Terminal Console. Type 'exit' to quit.\n")
        while True:
            try:
                line = input("gliacore> ").strip()
                if not line:
                    continue
                if line in ("exit", "quit", "q"):
                    break
                res = core.process(line)
                print(f"[{res['status']} | {res['total_latency_ms']}ms]")
                results = res.get("results", {})
                if "math" in results:
                    print(f"Result: {results['math'].get('result')}")
                elif "code" in results:
                    print(results['code'].get('synthesized_code'))
                elif "reasoning" in results:
                    print(results["reasoning"].get("text", ""))
            except (KeyboardInterrupt, EOFError):
                break
        core.close()
    else:
        host = getattr(args, "host", "127.0.0.1")
        port = getattr(args, "port", 8000)
        run(host=host, port=port)

if __name__ == "__main__":
    main()

NeuronServer = GliaCoreServer
