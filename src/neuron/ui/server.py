"""
Local Web Server & REST API for PROJECT: NEURON
Provides async endpoints for the Interactive Chat UI, live neural activity telemetry,
system monitoring, and model management using aiohttp.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any

from aiohttp import web

from neuron.core.engine import NeuralCore

STATIC_DIR = Path(__file__).parent / "static"


class NeuronServer:
    def __init__(self, db_path: str = "neuron_store.db"):
        self.core = NeuralCore(db_path=db_path)
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_post("/api/chat", self.handle_chat)
        self.app.router.add_get("/api/telemetry", self.handle_telemetry)
        self.app.router.add_get("/api/neurons", self.handle_neurons)
        self.app.router.add_get("/api/model", self.handle_model_info)
        self.app.router.add_post("/api/model/load", self.handle_model_load)
        self.app.router.add_post("/api/model/unload", self.handle_model_unload)
        self.app.router.add_get("/api/history", self.handle_history)
        self.app.router.add_static("/static", str(STATIC_DIR), name="static")

    async def handle_index(self, request: web.Request) -> web.Response:
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            return web.Response(text="NEURON UI frontend not yet generated.", status=404)
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

            synthesized_text = "\n".join(parts) if parts else "Task processed successfully."

        response_payload = {
            "task_id": res["task_id"],
            "session_id": session_id,
            "status": res["status"],
            "category": res.get("category"),
            "consensus_score": res.get("consensus_score", 1.0),
            "total_latency_ms": res.get("total_latency_ms", 0.0),
            "response_markdown": synthesized_text,
            "raw_results": res.get("results", {}),
            "execution_timeline": res.get("execution_timeline", []),
            "hardware_telemetry": res.get("hardware_telemetry", {}),
            "synapse_telemetry": res.get("synapse_telemetry", {})
        }
        return web.json_response(response_payload)

    async def handle_telemetry(self, request: web.Request) -> web.Response:
        """Returns real-time system and GPU metrics."""
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

    def close(self) -> None:
        self.core.close()


def create_app() -> web.Application:
    server = NeuronServer()
    return server.app


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = NeuronServer()
    print("=" * 70)
    print("PROJECT: NEURON — INTERACTIVE CHAT INTERFACE & BACKEND")
    print(f"Target Hardware: NVIDIA RTX 2050 (4 GB VRAM) | 16 GB System RAM")
    print(f"Server URL: http://{host}:{port}")
    print("Press Ctrl+C to terminate.")
    print("=" * 70)
    try:
        web.run_app(server.app, host=host, port=port, print=None)
    finally:
        server.close()


if __name__ == "__main__":
    run()
