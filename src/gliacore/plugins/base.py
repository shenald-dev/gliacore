"""
Standardized Plugin & Extension Architecture for PROJECT: NEURON
Enables third-party micro-neurons and tools to be registered dynamically
without modifying the core orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class PluginManifest:
    name: str
    version: str
    author: str
    description: str
    capabilities: List[str]
    required_dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    max_memory_mb: float = 250.0
    timeout_sec: float = 5.0


class BasePlugin(ABC):
    """
    Abstract base class for all third-party NEURON extensions.
    """

    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.is_active: bool = False

    @abstractmethod
    def initialize(self) -> bool:
        """Called when plugin is loaded into the ecosystem."""
        pass

    @abstractmethod
    def execute(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability provided by this plugin."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Called when plugin is unloaded or server terminates."""
        pass

    def get_info(self) -> Dict[str, Any]:
        return asdict(self.manifest)


class PluginManager:
    """
    Central manager for discovery, permission validation, and dynamic registration of plugins.
    """

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}

    def register_plugin(self, plugin: BasePlugin) -> Dict[str, Any]:
        """Validate and activate a plugin instance."""
        manifest = plugin.manifest
        
        # Security validation: disallow dangerous permissions
        forbidden_perms = {"root", "unrestricted_shell", "raw_disk_write"}
        if any(p in forbidden_perms for p in manifest.permissions):
            return {
                "success": False,
                "error": f"Plugin '{manifest.name}' requested prohibited permissions: {manifest.permissions}"
            }

        success = plugin.initialize()
        if success:
            plugin.is_active = True
            self._plugins[manifest.name] = plugin
            return {"success": True, "plugin": manifest.name, "capabilities": manifest.capabilities}
        else:
            return {"success": False, "error": f"Plugin '{manifest.name}' initialization failed"}

    def execute_plugin(self, plugin_name: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Safely execute an action in the specified plugin."""
        plugin = self._plugins.get(plugin_name)
        if not plugin or not plugin.is_active:
            return {"success": False, "error": f"Plugin '{plugin_name}' is not registered or inactive"}

        try:
            return plugin.execute(action, payload)
        except Exception as e:
            return {"success": False, "error": f"Plugin execution error: {str(e)}"}

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins and manifests."""
        return [
            {
                "name": p.manifest.name,
                "version": p.manifest.version,
                "author": p.manifest.author,
                "capabilities": p.manifest.capabilities,
                "is_active": p.is_active
            }
            for p in self._plugins.values()
        ]

    def unload_plugin(self, plugin_name: str) -> bool:
        """Gracefully shutdown and deregister a plugin."""
        plugin = self._plugins.get(plugin_name)
        if plugin:
            plugin.shutdown()
            plugin.is_active = False
            del self._plugins[plugin_name]
            return True
        return False
