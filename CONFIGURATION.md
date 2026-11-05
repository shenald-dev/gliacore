# GliaCore 0.3.0 — Configuration & Environment Reference

This document outlines all configuration options, environment variables, hardware budget controls, database paths, and model configurations supported by **GliaCore 0.3.0**.

---

## 1. Environment Variables

All settings in GliaCore can be configured via environment variables. GliaCore respects modern `GLIACORE_*` variables first, falling back seamlessly to legacy `NEURON_*` variables if present.

| Environment Variable | Default Value | Description |
|---|---|---|
| `GLIACORE_MAX_VRAM_MB` | `3500.0` | Target usable VRAM ceiling in MB on consumer GPUs (e.g., RTX 2050 4GB). Prevents CUDA OOM. |
| `NEURON_MAX_VRAM_MB` | `3500.0` | Legacy fallback variable for VRAM ceiling if `GLIACORE_MAX_VRAM_MB` is unset. |
| `GLIACORE_DB_PATH` | `gliacore_store.db` | Primary SQLite database path for task logs, full-text knowledge storage, and audit logs. |
| `GLIACORE_MEMORY_DB_PATH` | `gliacore_memory.db`| SQLite database path for the 4-Tier Memory Hierarchy (Episodic, Semantic, Procedural). |
| `GLIACORE_HOST` | `127.0.0.1` | Bind host for the local REST API and GliaCore Studio web interface. |
| `GLIACORE_PORT` | `8000` | Bind port for the local REST API and GliaCore Studio web interface. |
| `GLIACORE_LOG_LEVEL` | `INFO` | Console log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `GLIACORE_SANDBOX_TIMEOUT`| `5.0` | Maximum subprocess execution timeout in seconds for code evaluation. |

---

## 2. Hardware Resource Supervisor Configuration

The `HardwareSupervisor` monitors physical and usable memory to guarantee system stability:

```python
from gliacore.core.hardware import HardwareSupervisor

# Initialize with custom VRAM budget
supervisor = HardwareSupervisor(target_usable_vram_mb=3200.0)

# Query current telemetry
telemetry = supervisor.get_telemetry()
print(f"Device: {telemetry.device_name}")
print(f"Total VRAM: {telemetry.total_mb} MB")
print(f"Usable Headroom: {telemetry.free_usable_mb} MB")

# Check if an operation fits within safety boundaries
if supervisor.can_allocate_vram(500.0):
    print("Safe to allocate 500 MB")
else:
    print("Allocation rejected; falling back to CPU")
```

### Safety Headroom Formula:
$$\text{Free Usable VRAM} = \min(\text{Physical Free VRAM}, \text{Target Usable VRAM} - \text{Allocated VRAM}) - \text{500 MB Buffer}$$

---

## 3. Database Discovery & Auto-Fallback Policy

When starting without an explicit database path, GliaCore executes the following auto-discovery hierarchy:

1. **Storage Database:**
   - If `gliacore_store.db` exists in the working directory $\to$ bind to it.
   - Else if legacy `neuron_store.db` exists $\to$ bind to it and preserve past data.
   - Else $\to$ create `gliacore_store.db`.

2. **Memory Database:**
   - If `gliacore_memory.db` exists in the working directory $\to$ bind to it.
   - Else if legacy `neuron_memory.db` exists $\to$ bind to it and preserve past data.
   - Else $\to$ create `gliacore_memory.db`.

All SQLite connections enforce:
- `PRAGMA journal_mode = WAL;` (Write-Ahead Logging for high concurrency)
- `PRAGMA synchronous = NORMAL;`
- Connection-level re-entrant mutex locks (`threading.RLock`) to prevent database table locks under multi-worker concurrency.

---

## 4. Supported Foundation Models Catalog

Foundation models are managed by `ModelRunner` in `src/gliacore/core/model_runner.py`:

| Model Identifier | HuggingFace Repo | Required VRAM | Target Device | Quantization | Context Window |
|---|---|---|---|---|---|
| `qwen-0.5b` | `Qwen/Qwen2.5-0.5B-Instruct` | 650 MB | GPU / CPU fallback | 4-bit / FP32 | 2,048 tokens |
| `qwen-1.5b` | `Qwen/Qwen2.5-1.5B-Instruct` | 1,450 MB | GPU / CPU fallback | 4-bit / FP32 | 2,048 tokens |

### Loading Models via API:
```bash
curl -X POST http://127.0.0.1:8000/api/model/load \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen-0.5b", "force_cpu": false}'
```

### Unloading Models & Purging VRAM:
```bash
curl -X POST http://127.0.0.1:8000/api/model/unload
```

---

## 5. Adaptive Router Configuration

The `AdaptiveRouter` classifies task difficulty to optimize execution speed vs. reasoning depth:

- **SIMPLE ($\le 0.35$ complexity score):**
  - Trivial arithmetic, simple definitions, reflex queries.
  - Skips cognitive planner; routes directly to specialist neuron or reflex.
  - Typical latency: $1.5$–$3.5$ ms.
- **MODERATE ($0.35$–$0.70$ complexity score):**
  - Multi-step algebra, code synthesis, single-file analysis.
  - Invokes AST validation and generate-and-verify reflection loop.
  - Typical latency: $20$–$50$ ms.
- **COMPLEX ($> 0.70$ complexity score):**
  - Multi-part composite questions, autonomous agent goals, multi-document evidence synthesis.
  - Activates cognitive planning DAG, full synapse consensus, 4-tier memory retrieval.
  - Typical latency: $80$–$180$ ms.
