# GLIACORE MIGRATION GUIDE — Upgrading from NEURON to GliaCore 0.3.0

## 1. Overview & Migration Philosophy

PROJECT: NEURON has transitioned to **GliaCore 0.3.0**. This migration preserves 100% of the underlying architecture, test coverage, benchmark reproducibility, and existing user data while elevating the platform to a distinctive, unpolluted, and legally defensible brand.

GliaCore follows a **Zero-Disruption Migration Philosophy**:
1. **Zero Data Loss**: Existing SQLite database files (`neuron_store.db`, `neuron_memory.db`) are automatically detected and loaded if new GliaCore databases do not yet exist.
2. **Backward-Compatible Imports**: Legacy `import neuron` and `from neuron...` statements continue functioning via automated alias stubs with gentle deprecation notices.
3. **No Redundant Weight Downloads**: Model runner checkpoints and cache paths fall back transparently to previous directories.
4. **Preserved Architectural Taxonomy**: Specialized computational units remain designated as *Neurons*, binary channels remain designated as *Synapses*, and memory structures remain fully compatible.

---

## 2. Identity Mapping Reference

| Component / Layer | Legacy NEURON 0.x | New GliaCore 0.3.0 Standard | Backward Compatibility Guarantee |
|---|---|---|---|
| **Distribution Package** | `neuron-ai` | `gliacore-ai` | Seamless editable upgrade via `pip install -e .` |
| **Python Namespace** | `neuron` | `gliacore` | `import neuron` emits `FutureWarning` and proxies `gliacore` |
| **Primary Engine Class** | `NeuralCore` | `GliaCore` (aliased to `NeuralCore`) | Both `GliaCore` and `NeuralCore` work identically |
| **CLI Entry Point** | `python -m neuron.ui.server` | `gliacore` / `python -m gliacore.ui.server` | Legacy `neuron` CLI alias preserved in `pyproject.toml` |
| **Environment Prefix** | `NEURON_MAX_VRAM_MB` | `GLIACORE_MAX_VRAM_MB` | Falls back to `NEURON_*` if `GLIACORE_*` is unset |
| **Episodic Memory DB** | `neuron_memory.db` | `gliacore_memory.db` | Auto-detects and loads `neuron_memory.db` if present |
| **Task History DB** | `neuron_store.db` | `gliacore_store.db` | Auto-detects and loads `neuron_store.db` if present |
| **Default Web UI URL** | `http://127.0.0.1:8000` | `http://127.0.0.1:8000` | Fully compatible |

---

## 3. Package & Code Migration Steps

### Step 1: Update Your Python Imports
Update your codebase to import directly from the new `gliacore` namespace:

#### Before (Legacy):
```python
from neuron.core.engine import NeuralCore

core = NeuralCore()
res = core.process("Calculate 450 * 32")
core.close()
```

#### After (GliaCore 0.3.0 Standard):
```python
from gliacore.core.engine import GliaCore

core = GliaCore()
res = core.process("Calculate 450 * 32")
core.close()
```

*(Note: `NeuralCore` remains exported from `gliacore.core.engine` as an alias for complete backward compatibility).*

### Step 2: Environment Variable Updates
Update any shell profiles or container environments:

```bash
# Old
export NEURON_MAX_VRAM_MB=3500
export NEURON_DEVICE="cuda:0"

# New (Recommended)
export GLIACORE_MAX_VRAM_MB=3500
export GLIACORE_DEVICE="cuda:0"
```

### Step 3: Re-install Package in Editable Mode
From the project root:
```bash
pip install -e .
```

---

## 4. Automatic Database Discovery & Data Preservation

GliaCore automatically guards existing data. When initializing `GliaCore(db_path=None, memory_db_path=None)`:
1. If `gliacore_store.db` exists, it is loaded.
2. If `gliacore_store.db` does not exist but `neuron_store.db` is present, GliaCore automatically binds to `neuron_store.db` so no historical task records are lost.
3. If neither exists, `gliacore_store.db` is initialized.
4. The same discovery applies to `gliacore_memory.db` vs `neuron_memory.db`.

---

## 5. Optional Local Directory Rename

During development, the working directory remains `D:\neuron`. If you wish to rename your local directory to `D:\gliacore`, follow these safe steps:

```bash
# 1. Close active terminals and web UI servers running inside D:\neuron
# 2. In PowerShell or Command Prompt:
Rename-Item -Path "D:\neuron" -NewName "D:\gliacore"

# 3. Enter the renamed directory and refresh the pip editable link:
Set-Location "D:\gliacore"
pip install -e .

# 4. Run tests to confirm seamless operation:
python -m pytest tests -v
```
