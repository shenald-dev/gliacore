# PLUGIN ARCHITECTURE — Standardized Extension & Permission Model

## 1. Executive Summary

PROJECT: NEURON 0.3.0 introduces a **Standardized Plugin Architecture** (`src/neuron/plugins/base.py`) that allows third-party developers and domain specialists to extend NEURON's computational capabilities without modifying the core orchestrator or compromising the 4 GB VRAM boundary.

Plugins are treated as untrusted extensions governed by strict declarative manifests, fine-grained capability permissions, and lifecycle isolation.

---

## 2. Plugin Manifest Specification

Every plugin must define a static `PluginManifest` declaring its identity, dependencies, author, version, and required permissions:

```python
@dataclass
class PluginManifest:
    name: str                       # Unique identifier (e.g., 'statistics_toolkit')
    version: str                    # Semantic version (e.g., '1.0.0')
    description: str                # Human-readable capability summary
    author: str                     # Author name or organization
    required_permissions: List[str] # List of declared permissions
    tags: List[str]                 # Search & classification tags
    entry_point: str                # Qualified Python class path
```

---

## 3. Fine-Grained Permission System

Plugins cannot access system resources by default. NEURON enforces an explicit permission whitelist:

| Permission Flag | Description | Enforced Boundary |
|---|---|---|
| `compute` | Allows in-process CPU computations (NumPy, SciPy). | CPU only; bounded memory and execution time. |
| `filesystem:read` | Allows reading local workspace or reference files. | Path validation prevents directory traversal out of workspace. |
| `filesystem:write`| Allows saving generated reports or models. | Isolated to designated workspace export folders. |
| `hardware:read`   | Allows inspecting VRAM/RAM telemetry. | Read-only access to `HardwareSupervisor` metrics. |
| `network:egress`  | Allows outbound HTTP/REST calls. | Disabled by default. Blocked unless explicitly approved. |

If a plugin attempts to invoke an operation without declaring the matching permission in its manifest, `PluginManager.execute()` immediately raises a `PermissionError` and halts execution.

---

## 4. Lifecycle Hooks & Management

Plugins implement the `BasePlugin` abstract interface:

```python
class BasePlugin(ABC):
    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.is_active = False

    @abstractmethod
    def on_load(self, core: Any) -> bool:
        """Called during registration. Perform pre-flight validation."""
        pass

    @abstractmethod
    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a declared plugin capability."""
        pass

    @abstractmethod
    def on_unload(self) -> None:
        """Cleanup transient state, buffers, or open descriptors."""
        pass
```

### Dynamic Registration Lifecycle
1. **Manifest Validation**: `PluginManager.register_plugin()` verifies version formatting, ensures required manifest fields are non-empty, and checks for name collisions.
2. **Permission Check**: Verifies that declared permissions are supported by the runtime environment.
3. **Activation Hook**: Calls `.on_load(core)`. If the hook returns `False` or raises an exception, the plugin is rejected.
4. **Invocation**: Core and autonomous agents discover plugins via `PluginManager.list_plugins()` and dispatch requests via `PluginManager.execute_plugin()`.
5. **Teardown**: Calls `.on_unload()` when unregistering or shutting down the application.

---

## 5. Reference Implementation: Statistics Toolkit

The reference `StatisticsPlugin` (`src/neuron/plugins/statistics_plugin.py`) delivers high-performance numerical statistics without LLM hallucination:

```python
manifest = PluginManifest(
    name="statistics_toolkit",
    version="0.3.0",
    description="High-performance NumPy descriptive and matrix statistics engine",
    author="NEURON Research",
    required_permissions=["compute"],
    tags=["statistics", "numpy", "math"],
    entry_point="neuron.plugins.statistics_plugin.StatisticsPlugin"
)
```

Supported actions:
- `summary_stats`: Computes mean, median, variance, standard deviation, min, max, and quantiles (P25, P75).
- `correlation`: Calculates Pearson product-moment correlation matrix for multi-dimensional series.
- `cosine_similarity`: Computes high-speed cosine vector alignment between embeddings.

All calculations execute in under 0.5 ms using vectorized NumPy operations on CPU.
