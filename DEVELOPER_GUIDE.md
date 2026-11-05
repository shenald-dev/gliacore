# GliaCore 0.3.0 — Developer & Architecture Extension Guide

This guide is intended for developers, contributors, and researchers extending **GliaCore 0.3.0** with custom neurons, deterministic tools, and external plugins.

---

## 1. Codebase Directory Organization

```
D:\neuron\
├── pyproject.toml              # Build metadata, entrypoints, dependencies
├── README.md                   # Project overview & quickstart
├── LICENSE                     # GNU General Public License v3.0
├── src\
│   ├── gliacore\               # Primary namespace (GliaCore 0.3.0)
│   │   ├── core\               # Orchestrator, HardwareSupervisor, ModelRunner
│   │   ├── synapse\            # Binary MessagePack bus & IPC messages
│   │   ├── neurons\            # Specialist micro-neurons (Math, Coder, Reflex, Planner)
│   │   ├── reasoning\          # Generate-and-verify reflection loop
│   │   ├── routing\            # Adaptive difficulty-calibrated router
│   │   ├── memory\             # 4-tier memory hierarchy & SQLite knowledge store
│   │   ├── agent\              # DAG autonomous planner and step executor
│   │   ├── tools\              # SymPy, NumPy, AST parser, Code sandbox, Document indexer
│   │   ├── plugins\            # Third-party plugin architecture & permission sandbox
│   │   ├── learning\           # Experience-based self-improvement engine
│   │   └── ui\                 # Async REST server (aiohttp) and Studio HTML/JS frontend
│   └── neuron\                 # Backward-compatible shim delegating to gliacore
├── tests\                      # Pytest unit, integration, and E2E workflow test suites
└── benchmarks\                 # Reproducible 5-way benchmark suites & ablation studies
```

---

## 2. Authoring a Custom Specialist Neuron

All neurons inherit from `BaseNeuron` in `src/gliacore/neurons/base.py`:

```python
from typing import Dict, Any
from gliacore.neurons.base import BaseNeuron
from gliacore.synapse.bus import SynapseBus
from gliacore.synapse.messages import SynapseMessage, MessageType

class WeatherNeuron(BaseNeuron):
    def __init__(self, bus: SynapseBus = None):
        super().__init__(
            neuron_id="neuron_weather_01",
            name="Weather Specialist Unit",
            specialization="meteorology",
            bus=bus
        )

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        city = payload.get("city", "Unknown")
        # Perform computation or verified retrieval
        return {
            "city": city,
            "forecast": "Clear skies, 22°C",
            "confidence": 0.95
        }
```

### Registering Your Neuron:
```python
from gliacore.core.engine import GliaCore

core = GliaCore()
weather_unit = WeatherNeuron(bus=core.synapse_bus)
core.registry.register(weather_unit)
```

---

## 3. Creating a GliaCore Plugin

Plugins allow external modules to register new capabilities with declared security permissions:

```python
from typing import Dict, Any
from gliacore.plugins.base import BasePlugin, PluginManifest

class CryptoHashPlugin(BasePlugin):
    def __init__(self):
        manifest = PluginManifest(
            name="crypto_hasher",
            version="1.0.0",
            author="DevTeam",
            description="Computes SHA256 cryptographic digests",
            capabilities=["sha256_hash"],
            permissions=["read_only"]  # Prohibited permissions: "root", "unrestricted_shell", "raw_disk_write"
        )
        super().__init__(manifest)

    def initialize(self) -> bool:
        return True

    def execute(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        import hashlib
        if action == "sha256_hash":
            text = payload.get("text", "")
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            return {"success": True, "digest": digest}
        return {"success": False, "error": f"Unknown action {action}"}

    def shutdown(self) -> None:
        pass
```

---

## 4. Coding Standards & Review Guidelines

1. **Hardware-First Guardrails:** Never make allocations exceeding the 3,500 MB VRAM ceiling on RTX 2050. Always query `self.hardware.can_allocate_vram(size_mb)`.
2. **Deterministic Precedence:** If a problem can be solved symbolically (SymPy, AST, regex, SQLite FTS), solve it deterministically rather than making probabilistic LLM calls.
3. **Subprocess Isolation:** Never use `os.system()` or `subprocess.Popen(shell=True)`. Always use `CodeSandbox.execute()` with AST pre-screening and strict timeouts.
4. **Thread Safety & Relational Locks:** SQLite connections must be guarded with `threading.RLock()` and use WAL mode.

---

## 5. Running Developer Test Suites

```bash
# Run full unit and E2E test suite (43 items)
python -m pytest -o pythonpath=src tests -v

# Run with test statement coverage report
python -m pytest --cov=gliacore -o pythonpath=src tests

# Run adversarial penetration suite
python -m tests.security_adversarial_suite

# Run extreme stress test suite
python -m tests.stress_test_suite
```
