# GliaCore 0.3.0: An Edge-Optimized, Modular Micro-AI Collective Intelligence Ecosystem

[![Version: 0.3.0](https://img.shields.io/badge/version-0.3.0-blue.svg)](pyproject.toml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](pyproject.toml)
[![Hardware: NVIDIA RTX 2050 4GB](https://img.shields.io/badge/GPU-RTX%202050%20(4GB)-76B900.svg)](ARCHITECTURE.md)
[![Tests: 43 Passed](https://img.shields.io/badge/tests-43%20passed%20(100%25)-success.svg)](tests/)
[![Architecture: Glia--Neuron Collective](https://img.shields.io/badge/Architecture-Astrocyte--Neuron-purple.svg)](ARCHITECTURE.md)
[![Case Study: Dev.to](https://img.shields.io/badge/Case%20Study-Dev.to%20Article-black.svg)](https://dev.to/shenald/how-i-built-an-autonomous-zero-hallucination-micro-ai-on-an-entry-level-4gb-gpu-34dc)

> **PROJECT: GLIACORE 0.3.0** (formerly PROJECT: NEURON) is an experimental, open-source, resource-efficient micro-AI ecosystem designed to deliver distributed collective intelligence on extreme edge hardware (NVIDIA GeForce RTX 2050 4GB VRAM / 16GB System RAM).
>
> In biological neuroscience, neurons cannot compute, synchronize, or survive without the **glial network (astrocytes)**, which dynamically schedules metabolic resources, regulates synaptic transmission, and coordinates multi-neuron synchrony. 
>
> Rather than relying on a massive monolithic Large Language Model (LLM) or brittle API wrappers, **GliaCore** coordinates autonomous, specialized computational units (**Neurons**) over high-speed binary pathways (**Synapses**), orchestrated by an **Astrocyte Engine**, validated by a **Consensus & Verification Engine**, and backed by a **4-Tier Persistent Memory Hierarchy**.

---

## ⚡ 1-Click Launch (Windows 11)

No terminal commands needed. Simply double-click:
```cmd
run_gliacore.bat
```
*(Or `run_neuron.bat` for backward compatibility)*

The launcher automatically:
1. Bootstraps the local environment and sets `PYTHONPATH`.
2. Pre-loads the neural foundation model directly into **NVIDIA GPU VRAM**.
3. Starts the local async server at `http://127.0.0.1:8000`.
4. Launches your default web browser into the **GliaCore Studio** interactive UI.

---

## 1. Project Introduction & Biological Foundation

Traditional edge AI attempts to compress all human knowledge and reasoning into a single small language model (SLM, $\le 3$B parameters). On consumer hardware with 4 GB of VRAM, this causes catastrophic out-of-memory crashes, severe token throttling, and mathematical and syntactic hallucinations.

GliaCore inverts this paradigm through **biologically inspired neuro-symbolic modularity**:

```mermaid
graph TD
    User["User Prompt / GliaCore Studio Web UI"] --> Super["Hardware Supervisor\n(Strict 4GB VRAM Guard: Max 3.5GB Usable)"]
    Super --> Reflex["Reflex Neuron\n(<0.2 ms Regex & Security Screening Gate)"]
    
    subgraph GliaOrchestration ["GLIACORE 0.3.0 ASTROCYTE ENGINE"]
        Reflex -->|Clean| Router["Adaptive Neural Router\n(Difficulty: Simple / Moderate / Complex)"]
        Router --> MemHier["4-Tier Memory Hierarchy\n(Working, Episodic, Semantic, Procedural)"]
        
        MemHier --> Planner["Cognitive Planner Neuron\n(Selective Activation DAG)"]
        Planner --> SynapseBus["Synapse Binary Message Bus\n(MessagePack IPC / Pub-Sub)"]
        
        subgraph NeuronFleet ["Specialized Micro-Neuron Fleet"]
            MathN["Math Verifier Neuron\n(SymPy Symbolic Engine + GPU Derivation)"]
            CoderN["Coder Neuron\n(GPU Neural Synthesis + AST Parser + Sandbox)"]
            NumPyN["NumPy Numerical Engine\n(Descriptive Stats & Matrices)"]
            DocIdx["Document Indexer & Evidence Extractor"]
            RepoEx["Repository Explorer"]
            Plugins["Plugin Manager (Declared Permissions)"]
            ModelRunner["Model Runner (Qwen2.5 on NVIDIA RTX 2050 via CUDA/TF32)"]
        end
        
        SynapseBus <--> NeuronFleet
        NeuronFleet --> ReasonEngine["Advanced Reasoning Engine\n(Generate-and-Verify Reflection Loop)"]
        ReasonEngine --> Verifier["Consensus & Verification Engine\n(Contradiction Scoring)"]
    end
    
    Reflex -->|Security Threat| Blocked["Immediate Gateway Interception (<0.2 ms)"]
    Verifier --> Consolidate["Episodic Memory Consolidation (SQLite WAL)"]
    Consolidate --> FinalResponse["Verified Response + Execution Timeline"]
```

---

## 2. Why GliaCore Is Better Than Other AI Architectures

| Capability | Cloud Monoliths<br>*(ChatGPT / Claude / Gemini API)* | Local LLM Wrappers<br>*(Ollama / LM Studio / Llama.cpp)* | **GliaCore 0.3.0**<br>*(Astrocyte-Neuron Architecture)* |
| :--- | :--- | :--- | :--- |
| **Privacy & Offline** | ❌ Sends private data to third-party cloud servers | ⚠️ Text-only local generation | ** 100% Local, Private & Air-Gapped** |
| **Cost** | ❌ Expensive recurring subscription or per-token API fees |  Free | ** 100% Free & Open Source (GPLv3)** |
| **Math Precision** | ❌ Frequently hallucinates arithmetic on large numbers | ❌ Guesses tokens based on probabilistic weights | ** 0% Hallucination** (SymPy exact symbolic computation) |
| **Math Derivations** |  Probabilistic reasoning | ⚠️ Inconsistent token generation | ** Verified Hybrid** (Exact numerical + GPU step-by-step derivation) |
| **Code Reliability** | ⚠️ Often outputs syntax errors or unverified imports | ❌ No static analysis or runtime sandbox | ** AST Parser Validated + Isolated Sandbox Executed** |
| **Self-Repair** | ❌ Requires manual user reprompting when code fails | ❌ Blind generation with zero runtime feedback | ** Automated Reflection Loop** (Auto-corrects syntax bugs) |
| **Web & App Code** |  Generates markup | ⚠️ Often refuses or truncates | ** Full-Stack Synthesis** (HTML/CSS landing pages, JS, Python) |
| **Memory Persistence**| ⚠️ Web UI history only (opaque, untagged) | ❌ Zero persistence across restarts | ** 4-Tier Memory** (Persistent SQLite WAL databases) |
| **Hardware Safety** | N/A (Server-side) | ⚠️ Prone to hard CUDA Out-Of-Memory system crashes | ** Hardware Supervisor** (Strict 3,500 MB VRAM ceiling) |
| **Inference Speed** | ⚠️ Variable internet latency (1-5s) | ⚠️ Slow without GPU optimization | ** 18.3 tokens/sec** on CUDA cores (Ampere TF32 enabled) |
| **Security Guardrail**| ⚠️ Slow cloud content-moderation API | ❌ None (raw prompt execution) | ** <0.2 ms Reflex Gateway** (Blocks shell injection & fork bombs) |

---

## 3. Core Capabilities

- **Active NVIDIA GPU Neural Inference**: Leverages Qwen2.5 on CUDA with Ampere TensorFloat-32 (TF32) acceleration, generating dynamic, context-aware responses at **18.3 tokens/second**.
- **Neuro-Symbolic Dual Brain**: Blends the creative fluency of a local neural network with deterministic engines (SymPy for math, Python AST parser for syntax, isolated subprocess sandbox for runtime execution).
- **Full-Stack Web & Software Synthesis**: Generates complete, runnable deliverables (Python functions, data structures, and complete modern HTML/CSS landing pages) without RLHF refusal barriers.
- **Generate-and-Verify Reflection Loop**: Automatically detects syntax defects (missing colons, unbalanced parentheses) and repairs them in an internal reflection loop before runtime delivery.
- **4-Tier Cognitive Memory Hierarchy**: Integrates Working Memory (live task scratchpad), Episodic Memory (persistent SQLite task logs), Semantic Memory (indexed documents with citations), and Procedural Memory (executable tool recipes).
- **Controlled Autonomous Agent**: Decomposes high-level goals into Directed Acyclic Graphs (DAGs) with sub-step dependency tracking, atomic checkpoints, and sub-second user cancellation.
- **Hardware-Guarded Containment**: Continuously monitors GPU VRAM and host RAM, strictly guarding against CUDA OOM crashes by maintaining a 3,500 MB safe ceiling on 4GB consumer GPUs.

---

## 4. Hardware Environment & Verified RTX 2050 Telemetry

All architectural decisions in GliaCore are engineered and tested around real consumer laptop hardware:

| Component | Physical Specification | Operating Budget / Status | Verification Notes |
|---|---|---|---|
| **GPU** | NVIDIA GeForce RTX 2050 Laptop | **3,500 MB** safe usable ceiling | ~523 MB reserved for Windows OS / DWM display |
| **CUDA Compute** | GA107 Ampere (Compute Capability 8.6) | 16 Streaming Multiprocessors | TF32 Tensor Core acceleration activated |
| **VRAM Allocated** | 4,096 MB physical | **942.32 MB** allocated in FP16 | Over 2,500 MB free headroom for KV-cache |
| **Inference Speed**| Local CUDA cores | **18.28 tokens/second** | Measured across multi-turn reasoning |
| **System RAM** | 16,384 MB physical | **14,000 MB** max allocation | Host OS stability guaranteed |
| **Security Gate** | Sub-millisecond Regex & AST filter | **<0.2 ms** latency | 100% of destructive shell payloads blocked |

---

## 5. Empirical 5-Way Benchmark Comparison (N = 50 Tasks)

Independently benchmarked across 50 diverse evaluation tasks spanning arithmetic, algebra, code synthesis, AST analysis, composite workflows, system planning, prompt injection, and reasoning:

| Metric | Monolith Raw (A) | Isolated Neurons (B) | NEURON Phase 2 (C) | GliaCore 0.3.0 AR (D) | GliaCore 0.3.0 Full (E) |
|---|---|---|---|---|---|
| **Task Accuracy (%)** | 54.0% | 70.0% | 92.0% | **96.0%** | **96.0%** |
| **Hallucination Rate (%)** | 22.0% | 10.0% | **0.0%** | 4.0% | **0.0%** (Math) |
| **Failure Rate (%)** | 46.0% | 30.0% | 8.0% | **4.0%** | **4.0%** |
| **Mean Latency (ms)** | 3.77 ms | 1.79 ms | 24.63 ms | 96.47 ms | 102.22 ms |
| **Median Latency (ms)** | 1.62 ms | 0.30 ms | 2.36 ms | 74.91 ms | 79.03 ms |
| **P95 Latency (ms)** | 2.88 ms | 4.05 ms | 80.93 ms | 154.58 ms | 185.35 ms |
| **Peak VRAM Allocated** | 150.0 MB | 26.0 MB | 26.0 MB | **942.3 MB** | **942.3 MB** |
| **Security Interception**| 0% Blocked | 0% Blocked | 100% Intercepted | **100% Intercepted** | **100% Intercepted** |
| **Deterministic Offload**| 0% | 50% | 100% | **100%** | **100%** |
| **Accumulated Memory** | 0 | 0 | 0 | 0 | **46 Items** |

---

## 6. Quickstart & Installation

### Installation
```bash
git clone https://github.com/shenald-dev/gliacore.git
cd gliacore
pip install -e .
```

### Launch Interactive Web Studio (1-Click)
```bash
# On Windows: Double-click run_gliacore.bat
# Or run from terminal:
python -m gliacore.ui.server
# Open browser at: http://127.0.0.1:8000
```

### Run Unit & End-to-End Tests (43/43 Passing)
```bash
python -m pytest -o pythonpath=src tests -v
```

### Run Phase 3 5-Way Benchmark Suite
```bash
python benchmarks/phase3_benchmark.py
```

---

## 7. Python SDK Quickstart

### Native GliaCore 0.3.0 Standard
```python
from gliacore.core.engine import GliaCore

core = GliaCore(auto_load_model=True)

# 1. Mathematical problem with exact SymPy result + GPU derivation
result = core.process("Calculate 25 * 18 + 140 / 7")
print(result["results"]["math"]["result"]["numeric"])  # 470.0
print(result["results"]["reasoning"]["text"])           # Full step-by-step breakdown

# 2. Code synthesis with AST validation and sandbox execution
code_res = core.process("Write a Python function to check if a string is a palindrome.")
print(code_res["results"]["code"]["synthesized_code"])
print(code_res["results"]["code"]["syntax_valid"])      # True

# 3. Security guardrail interception
sec_res = core.process("rm -rf / --no-preserve-root")
print(sec_res["status"])                               # BLOCKED (<0.2 ms)

core.close()
```

### Legacy Backward-Compatible Import
Existing code using `import neuron` continues functioning seamlessly without changes:
```python
# Emits a polite FutureWarning recommending upgrade to gliacore
from neuron.core.engine import NeuralCore

core = NeuralCore()
result = core.process("Calculate 18 * (45 + 125)")
print(result["results"]["math"]["result"]["numeric"])
core.close()
```

---

## 8. Interactive 6-Workspace Web UI (GliaCore Studio)

GliaCore Studio provides an intuitive, high-performance web dashboard at `http://127.0.0.1:8000`:
- **Workspace 1 (Chat & Execution Timeline)**: Real-time chat with visual execution telemetry cards for each stage.
- **Workspace 2 (Memory Hierarchy Explorer)**: Inspect, query, and tag working, episodic, semantic, and procedural memories.
- **Workspace 3 (Autonomous Agent Planner)**: Submit multi-step goals, preview DAG dependencies, inspect checkpoints, and cancel active jobs.
- **Workspace 4 (Knowledge Document Ingestion)**: Ingest local documents into SQLite with full-text search and evidence extraction.
- **Workspace 5 (Telemetry & Self-Improvement)**: Live VRAM/RAM gauges and automatic bottleneck optimization proposals.
- **Workspace 6 (Model & Neuron Fleet)**: Inspect specialist neuron states, device allocation, and model loading.

---

## 9. Technical Documentation Directory

- [`DEVTO_CASE_STUDY.md`](https://dev.to/shenald/how-i-built-an-autonomous-zero-hallucination-micro-ai-on-an-entry-level-4gb-gpu-34dc): **Deep-dive Dev.to publication case study** on building a 4GB edge AI ecosystem.
- [`BRAND_RESEARCH.md`](BRAND_RESEARCH.md): Full naming study, namespace collisions, weighted ranking, and selection analysis.
- [`BRAND_IDENTITY.md`](BRAND_IDENTITY.md): Visual identity, Astrocyte Core logo, color palette, and taxonomy conventions.
- [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md): Step-by-step upgrade guide, backward compatibility stubs, and database preservation.
- [`ADVANCED_INTELLIGENCE.md`](ADVANCED_INTELLIGENCE.md): System architecture, dynamic neuron selection, and collective intelligence.
- [`REASONING_ENGINE.md`](REASONING_ENGINE.md): Multi-stage reasoning, generate-and-verify reflection loop, and syntax self-repair.
- [`MEMORY_EVOLUTION.md`](MEMORY_EVOLUTION.md): 4-tier memory hierarchy specification, scoring formulas, and consolidation daemon.
- [`ADAPTIVE_ROUTING.md`](ADAPTIVE_ROUTING.md): Difficulty computation formulas and selective neuron dispatch policies.
- [`AUTONOMOUS_EXECUTION.md`](AUTONOMOUS_EXECUTION.md): Controlled DAG agent, cancellation protocols, and state checkpoints.
- [`PHASE3_BENCHMARKS.md`](PHASE3_BENCHMARKS.md): Comprehensive empirical evaluation results across 50 benchmark tasks.
- [`PHASE3_SECURITY_REPORT.md`](PHASE3_SECURITY_REPORT.md): Threat modeling, 10/10 attack vector interceptions, and sandbox guarantees.

---

## 10. License & Compliance

This software is released under the **GNU General Public License v3.0 (GPLv3)**.

### Model License Compliance
Upstream foundation models (e.g. `Qwen2.5-0.5B-Instruct` and `Qwen2.5-1.5B-Instruct`) are distributed under the permissive **Apache 2.0** license. Model weights are strictly decoupled from GliaCore application code and loaded via standard external runtime checkpoints, maintaining total compliance with both GPLv3 and Apache 2.0 terms.
