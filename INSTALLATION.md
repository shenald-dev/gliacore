# GliaCore 0.3.0 — Installation & Environment Setup Guide

This guide provides end-to-end instructions for installing, configuring, and verifying **GliaCore 0.3.0** on consumer hardware running Windows 11, Linux, or macOS.

---

## 1. System Requirements

### Hardware Specifications
| Component | Minimum Specification | Recommended Specification (Benchmarked) |
|---|---|---|
| **Operating System** | Windows 10/11 64-bit, Ubuntu 22.04+, macOS 13+ | Windows 11 64-bit |
| **GPU** | Optional (Runs in CPU fallback mode) | NVIDIA GeForce RTX 2050 (4 GB VRAM) or higher |
| **CUDA Driver** | NVIDIA Driver 535+ (CUDA 12.1+) | NVIDIA Driver 550+ (CUDA 12.4) |
| **System RAM** | 8 GB RAM | 16 GB DDR4/DDR5 RAM |
| **Disk Space** | 2.5 GB for environment + dependencies | 10 GB (including model checkpoints) |
| **Python** | Python 3.10, 3.11, or 3.12 | Python 3.11.0 64-bit |

---

## 2. Prerequisites

### Windows 11
1. Install Python 3.11 from [python.org](https://www.python.org/downloads/) (ensure **"Add python.exe to PATH"** is checked).
2. Install NVIDIA CUDA Toolkit 12.1 or 12.4 (if GPU acceleration is desired).
3. Ensure Git is installed:
   ```powershell
   git --version
   ```

### Linux (Ubuntu / Debian)
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-dev git build-essential
```

---

## 3. Fresh Installation Workflow

### Step 1: Clone Repository
```bash
git clone https://github.com/gliacore-ai/gliacore.git
cd gliacore
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install PyTorch with CUDA Support (Optional for GPU)
If you have an NVIDIA GPU, install the CUDA-enabled PyTorch build first:
```bash
# For CUDA 12.4
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# For CPU-only environments
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Step 4: Install GliaCore in Editable Mode
```bash
pip install -e .
```

To install development and testing tools (pytest, pytest-cov, ruff):
```bash
pip install -e ".[dev]"
```

---

## 4. Verification & Self-Test

Verify that GliaCore is correctly installed by running the unit and end-to-end test suite:

```bash
# Run full 43-test suite
python -m pytest -o pythonpath=src tests -v
```

Expected result:
```
============================= 43 passed in 16.83s =============================
```

### Run Adversarial Security Verification:
```bash
python -m tests.security_adversarial_suite
```

### Run 5-Way Architectural Benchmark:
```bash
python benchmarks/phase3_benchmark.py
```

---

## 5. Starting GliaCore Studio

Launch the interactive local web dashboard:
```bash
# CLI entrypoint
gliacore

# Or module execution
python -m gliacore.ui.server
```

Open your browser at `http://127.0.0.1:8000`.

---

## 6. Upgrading from Legacy PROJECT: NEURON

GliaCore provides 100% backward compatibility for previous installations:
- Existing databases (`neuron_store.db` and `neuron_memory.db`) are automatically detected and preserved.
- Code using `import neuron` continues to work with a polite `FutureWarning`.
- Environment variable `NEURON_MAX_VRAM_MB` is automatically honored if `GLIACORE_MAX_VRAM_MB` is unset.

See [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md) for details.
