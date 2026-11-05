"""
Model Context Protocol (MCP) Server for GliaCore.
Exposes GliaCore's deterministic symbolic engines (Reflex gate, SymPy math, AST code sandbox,
4-tier memory, and end-to-end task solver) to Claude Desktop, Cursor, and any MCP-compliant client.
Supports both stdio transport (JSON-RPC over stdin/stdout) and HTTP/SSE transport.
"""

import sys
import json
import logging
from typing import Dict, Any, Optional, Callable

from gliacore.mcp.protocol import (
    LATEST_PROTOCOL_VERSION,
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    MCPTool,
    JSONRPCResponse,
)

logger = logging.getLogger("gliacore.mcp")


class GliaCoreMCPServer:
    """
    Standard MCP 2024-11-05 Server exposing GliaCore micro-AI tools.
    """

    def __init__(self, core=None):
        if core is None:
            from gliacore.core.engine import GliaCore
            self.core = GliaCore(auto_load_model=False)
            self._owns_core = True
        else:
            self.core = core
            self._owns_core = False

        self._tools: Dict[str, MCPTool] = {}
        self._tool_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._register_default_tools()

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """Register a new MCP tool with its metadata and invocation handler."""
        tool = MCPTool(name=name, description=description, input_schema=input_schema)
        self._tools[name] = tool
        self._tool_handlers[name] = handler

    def _register_default_tools(self) -> None:
        """Register standard GliaCore symbolic & neural tools."""

        # 1. Reflex & Security Scan
        self.register_tool(
            name="gliacore_reflex_scan",
            description="Sub-millisecond prompt-injection, adversarial shell, and security screening (<0.2ms latency).",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "User or agent input string to inspect for safety risks and command escapes."
                    }
                },
                "required": ["prompt"]
            },
            handler=self._handle_reflex_scan
        )

        # 2. Math & Symbolic Equation Solving (SymPy)
        self.register_tool(
            name="gliacore_math_solve",
            description="Exact mathematical evaluation, algebraic equation solving, and calculus derivation via SymPy with zero hallucination.",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Natural language or algebraic prompt (e.g. 'Solve 3*x^2 - 12 = 0' or 'Calculate 2^16 / 8')."
                    }
                },
                "required": ["prompt"]
            },
            handler=self._handle_math_solve
        )

        # 3. Secure AST Python Code Sandbox
        self.register_tool(
            name="gliacore_code_sandbox",
            description="Execute Python code in an isolated subprocess sandbox with AST syntax and security verification.",
            input_schema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code snippet to execute safely."
                    },
                    "timeout_sec": {
                        "type": "number",
                        "description": "Maximum execution time before termination (default 5.0 seconds).",
                        "default": 5.0
                    }
                },
                "required": ["code"]
            },
            handler=self._handle_code_sandbox
        )

        # 4. 4-Tier Memory Query
        self.register_tool(
            name="gliacore_memory_query",
            description="Query GliaCore's 4-tier persistent memory hierarchy (working, episodic, semantic, archival).",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword or conceptual query."
                    },
                    "tier": {
                        "type": "string",
                        "description": "Optional specific memory tier to search (working, episodic, semantic, archival).",
                        "enum": ["working", "episodic", "semantic", "archival"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memory items to return (default 5).",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_memory_query
        )

        # 5. End-to-End GliaCore Collective Intelligence Solver
        self.register_tool(
            name="gliacore_solve",
            description="End-to-end task processing through GliaCore's neural-symbolic router, multi-stage reflection loop, and consensus verifier.",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Task, question, or problem to solve."
                    }
                },
                "required": ["prompt"]
            },
            handler=self._handle_solve
        )

        # 6. Document Citations & Knowledge Indexer
        self.register_tool(
            name="gliacore_document_query",
            description="Query ingested documents for exact citations, grounded paragraphs, and evidence excerpts.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query term to find citations for in ingested files."
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_document_query
        )

        # 7. Real-Time Hardware & VRAM Telemetry
        self.register_tool(
            name="gliacore_system_telemetry",
            description="Get real-time GPU VRAM budget, system RAM, latency statistics, and registered neuron status.",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_telemetry
        )

    # Tool Handlers
    def _handle_reflex_scan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        prompt = args.get("prompt", "")
        res = self.core.reflex_neuron.run({"prompt": prompt})
        return res.get("result", {})

    def _handle_math_solve(self, args: Dict[str, Any]) -> Dict[str, Any]:
        prompt = args.get("prompt", "")
        res = self.core.math_neuron.run({"prompt": prompt})
        return res.get("result", {})

    def _handle_code_sandbox(self, args: Dict[str, Any]) -> Dict[str, Any]:
        code = args.get("code", "")
        timeout = float(args.get("timeout_sec", 5.0))
        res = self.core.coder_neuron.run({"code": code, "run_tests": True, "timeout_sec": timeout})
        return res.get("result", {})

    def _handle_memory_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query", "")
        tier = args.get("tier")
        limit = int(args.get("limit", 5))
        memories = self.core.memory.retrieve(query, tier=tier, limit=limit)
        return {"query": query, "count": len(memories), "memories": memories}

    def _handle_solve(self, args: Dict[str, Any]) -> Dict[str, Any]:
        prompt = args.get("prompt", "")
        res = self.core.process(prompt)
        # Simplify response for MCP output
        return {
            "task_id": res.get("task_id"),
            "status": res.get("status"),
            "category": res.get("category"),
            "difficulty": res.get("difficulty"),
            "consensus_score": res.get("consensus_score"),
            "total_latency_ms": res.get("total_latency_ms"),
            "results": res.get("results"),
            "reflection_repairs": res.get("reflection_repairs", [])
        }

    def _handle_document_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query", "")
        return self.core.document_indexer.query_evidence(query)

    def _handle_telemetry(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.core.get_system_telemetry()

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single JSON-RPC 2.0 MCP request and return the JSON-RPC response dict.
        Returns None for notifications (requests without an 'id').
        """
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Handle notifications (no response expected)
        if req_id is None and method == "notifications/initialized":
            return None

        # 1. initialize
        if method == "initialize":
            return JSONRPCResponse(
                id=req_id,
                result={
                    "protocolVersion": LATEST_PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "gliacore",
                        "version": "0.4.0",
                        "title": "GliaCore Edge Micro-AI Collective Intelligence"
                    }
                }
            ).to_dict()

        # 2. ping
        if method == "ping":
            return JSONRPCResponse(id=req_id, result={}).to_dict()

        # 3. tools/list
        if method == "tools/list":
            tools_list = [tool.to_dict() for tool in self._tools.values()]
            return JSONRPCResponse(id=req_id, result={"tools": tools_list}).to_dict()

        # 4. tools/call
        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name not in self._tools:
                return JSONRPCResponse(
                    id=req_id,
                    error={
                        "code": INVALID_PARAMS,
                        "message": f"Tool '{tool_name}' not found."
                    }
                ).to_dict()

            handler = self._tool_handlers[tool_name]
            try:
                result = handler(tool_args)
                result_text = json.dumps(result, indent=2, default=str)
                return JSONRPCResponse(
                    id=req_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ],
                        "isError": False
                    }
                ).to_dict()
            except Exception as e:
                return JSONRPCResponse(
                    id=req_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing tool '{tool_name}': {e}"
                            }
                        ],
                        "isError": True
                    }
                ).to_dict()

        # Unknown method
        if req_id is not None:
            return JSONRPCResponse(
                id=req_id,
                error={
                    "code": METHOD_NOT_FOUND,
                    "message": f"Method '{method}' is not supported by GliaCore MCP server."
                }
            ).to_dict()

        return None

    def run_stdio(self) -> None:
        """
        Run the MCP server in standard I/O mode, communicating over stdin/stdout.
        Compatible with Claude Desktop, Cursor, Continue, and VS Code MCP clients.
        """
        # Ensure stdout does not buffer output
        sys.stdout.reconfigure(line_buffering=True)
        
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except Exception as e:
                err_resp = JSONRPCResponse(
                    id=None,
                    error={"code": -32700, "message": f"Parse error: {e}"}
                ).to_dict()
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
                continue

            resp = self.handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

    def close(self) -> None:
        if self._owns_core and self.core:
            self.core.close()
