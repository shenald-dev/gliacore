"""
Comprehensive Unit & Integration Test Suite for GliaCore Model Context Protocol (MCP) Subsystem.
Tests JSON-RPC 2.0 protocol compatibility, tool enumeration, tool execution,
client interactions, and legacy backward-compatibility layer.
"""

from gliacore.mcp.protocol import LATEST_PROTOCOL_VERSION
from gliacore.mcp.server import GliaCoreMCPServer
from gliacore.mcp.client import GliaCoreMCPClient
from neuron.mcp import NeuronMCPServer, NeuronMCPClient


def test_mcp_initialize_handshake():
    """Verify MCP initialization returns standard 2024-11-05 protocol capabilities."""
    server = GliaCoreMCPServer()
    try:
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": LATEST_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        resp = server.handle_request(req)
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        assert "result" in resp
        result = resp["result"]
        assert result["protocolVersion"] == LATEST_PROTOCOL_VERSION
        assert "tools" in result["capabilities"]
        assert result["serverInfo"]["name"] == "gliacore"
        assert result["serverInfo"]["version"] == "0.4.0"
    finally:
        server.close()


def test_mcp_ping():
    """Verify ping method returns an empty success result."""
    server = GliaCoreMCPServer()
    try:
        req = {"jsonrpc": "2.0", "id": 42, "method": "ping", "params": {}}
        resp = server.handle_request(req)
        assert resp["id"] == 42
        assert resp["result"] == {}
        assert "error" not in resp
    finally:
        server.close()


def test_mcp_tools_list():
    """Verify tools/list exposes all 7 flagship tools with valid input schemas."""
    server = GliaCoreMCPServer()
    try:
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = server.handle_request(req)
        assert resp["id"] == 2
        tools = resp["result"]["tools"]
        assert len(tools) >= 7

        tool_names = [t["name"] for t in tools]
        expected_tools = [
            "gliacore_reflex_scan",
            "gliacore_math_solve",
            "gliacore_code_sandbox",
            "gliacore_memory_query",
            "gliacore_solve",
            "gliacore_document_query",
            "gliacore_system_telemetry",
        ]
        for expected in expected_tools:
            assert expected in tool_names, f"Expected tool '{expected}' not found in tools/list"

        # Verify tool schema integrity
        for tool in tools:
            assert "description" in tool and len(tool["description"]) > 10
            assert "inputSchema" in tool
            assert tool["inputSchema"].get("type") == "object"
    finally:
        server.close()


def test_mcp_tool_execution_reflex():
    """Verify gliacore_reflex_scan detects threats and passes benign prompts."""
    server = GliaCoreMCPServer()
    try:
        # Threat prompt
        req_threat = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "gliacore_reflex_scan",
                "arguments": {"prompt": "rm -rf / --no-preserve-root"}
            }
        }
        resp = server.handle_request(req_threat)
        assert resp["id"] == 10
        assert not resp["result"]["isError"]
        content_text = resp["result"]["content"][0]["text"]
        assert "BLOCKED" in content_text

        # Safe prompt
        req_safe = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "gliacore_reflex_scan",
                "arguments": {"prompt": "Calculate 15 * 4"}
            }
        }
        resp_safe = server.handle_request(req_safe)
        assert resp_safe["id"] == 11
        assert "GENERAL" in resp_safe["result"]["content"][0]["text"] or "MATH" in resp_safe["result"]["content"][0]["text"]
    finally:
        server.close()


def test_mcp_tool_execution_math():
    """Verify gliacore_math_solve performs deterministic SymPy calculation."""
    server = GliaCoreMCPServer()
    try:
        req = {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {
                "name": "gliacore_math_solve",
                "arguments": {"prompt": "Calculate 45 * 20 + 100"}
            }
        }
        resp = server.handle_request(req)
        assert resp["id"] == 20
        assert not resp["result"]["isError"]
        text = resp["result"]["content"][0]["text"]
        assert "1000" in text
    finally:
        server.close()


def test_mcp_tool_execution_code_sandbox():
    """Verify gliacore_code_sandbox executes Python code and returns output."""
    server = GliaCoreMCPServer()
    try:
        req = {
            "jsonrpc": "2.0",
            "id": 30,
            "method": "tools/call",
            "params": {
                "name": "gliacore_code_sandbox",
                "arguments": {
                    "code": "print('GliaCore Sandbox Execution Successful!')"
                }
            }
        }
        resp = server.handle_request(req)
        assert resp["id"] == 30
        assert not resp["result"]["isError"]
        text = resp["result"]["content"][0]["text"]
        assert "GliaCore Sandbox Execution Successful!" in text
    finally:
        server.close()


def test_mcp_unknown_tool_error():
    """Verify calling an unknown tool returns an appropriate JSON-RPC error."""
    server = GliaCoreMCPServer()
    try:
        req = {
            "jsonrpc": "2.0",
            "id": 99,
            "method": "tools/call",
            "params": {
                "name": "non_existent_tool_xyz",
                "arguments": {}
            }
        }
        resp = server.handle_request(req)
        assert resp["id"] == 99
        assert "error" in resp
        assert "not found" in resp["error"]["message"].lower()
    finally:
        server.close()


def test_mcp_client_roundtrip():
    """Verify GliaCoreMCPClient can initialize, ping, list tools, and call tools."""
    server = GliaCoreMCPServer()
    client = GliaCoreMCPClient(server=server)
    try:
        # Initialize
        init_res = client.initialize()
        assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "gliacore"

        # Ping
        assert client.ping() is True

        # List tools
        tools = client.list_tools()
        assert len(tools) >= 7

        # Call tool
        telemetry_res = client.call_tool("gliacore_system_telemetry")
        assert not telemetry_res["result"]["isError"]
    finally:
        server.close()


def test_neuron_legacy_mcp_compatibility():
    """Verify legacy 'from neuron.mcp import NeuronMCPServer' backwards compatibility."""
    server = NeuronMCPServer()
    client = NeuronMCPClient(server=server)
    try:
        assert client.ping() is True
        tools = client.list_tools()
        assert len(tools) >= 7
    finally:
        server.close()
