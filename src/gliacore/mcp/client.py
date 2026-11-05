"""
Model Context Protocol (MCP) Client for GliaCore.
Enables GliaCore agents to connect to external MCP servers (stdio or HTTP/in-process),
enumerate available tools, and invoke external tool capabilities dynamically.
"""

from typing import Dict, Any, List, Optional
from gliacore.mcp.protocol import LATEST_PROTOCOL_VERSION


class GliaCoreMCPClient:
    """
    Client interface to interact with MCP servers.
    Can wrap a local in-process MCPServer or communicate with external servers.
    """

    def __init__(self, server=None):
        self.server = server
        self.server_info: Dict[str, Any] = {}
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        self._request_counter: int = 1

    def initialize(self) -> Dict[str, Any]:
        """Perform MCP initialization handshake."""
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": LATEST_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": "gliacore-agent",
                    "version": "0.4.0"
                }
            }
        }
        resp = self._send(req)
        if "result" in resp:
            self.server_info = resp["result"].get("serverInfo", {})
        return resp

    def list_tools(self) -> List[Dict[str, Any]]:
        """Query server for list of available tools."""
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }
        resp = self._send(req)
        tools = resp.get("result", {}).get("tools", [])
        self.available_tools = {t["name"]: t for t in tools}
        return tools

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a tool on the MCP server."""
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        }
        return self._send(req)

    def ping(self) -> bool:
        """Ping server to verify connectivity."""
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "ping",
            "params": {}
        }
        resp = self._send(req)
        return "result" in resp and resp.get("error") is None

    def _next_id(self) -> int:
        cur = self._request_counter
        self._request_counter += 1
        return cur

    def _send(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to configured server."""
        if self.server is not None:
            res = self.server.handle_request(request)
            return res or {}
        raise RuntimeError("No MCP server connection configured for GliaCoreMCPClient.")
