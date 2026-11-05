# PROJECT: NEURON — Interactive Chat UI & API Guide

This guide documents the local setup, usage, architectural features, and REST API endpoints for the **NEURON Interactive Chat Interface**.

---

## 1. Quickstart & Launching the Interface

### Direct CLI Launch
To launch the NEURON local web server and user interface on your machine:

```bash
# Navigate to the repository
cd D:\neuron

# Start the interactive UI server
python -m neuron
```

By default, the server binds to `http://127.0.0.1:8000`.

### Custom Port or Interface
You can specify a custom port or host interface:

```bash
python -m neuron --host 127.0.0.1 --port 8080
```

Once running, open your web browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 2. Interface Walkthrough

```
+-----------------------------------------------------------------------------------------+
| [N] NEURON [RTX 2050] |  Status: ONLINE  [Qwen2.5 Micro-Core]   | [Activity] [Clear]     |
+-----------------------+-----------------------------------------+-----------------------+
|  + New Conversation   |                                         | [Tab: Neural Activity]|
|                       |  User: Solve 4*x - 17 = 43              | - Stage 1: Reflex     |
|  - Current Session    |  Neuron: [SUCCESS] [Consensus: 1.0]     | - Stage 2: Planner    |
|                       |  ### Mathematical Verification (SymPy)  | - Stage 3: Math (Sym) |
|                       |  - Equation: 4*x - 17 = 43              | - Stage 4: Consensus  |
|                       |  - Solutions: [15]                      |                       |
|  [VRAM: 26/3500 MB]   |  [Latency: 78.4ms | VRAM: 26MB]         | [Tab: Telemetry]      |
|  [RAM: 6,400 MB Free] |                                         | - GPU VRAM Usage      |
|                       |  [Input: Ask NEURON a task... ] [Send]  | - System RAM & CPU    |
+-----------------------+-----------------------------------------+-----------------------+
```

### A. Main Chat Area
- **Markdown & Syntax Highlighting**: Automatically formats mathematical equations, structured tables, and Python code blocks.
- **One-Click Code Copy**: Every synthesized code snippet includes an interactive copy button.
- **Verification Pills**: Every response displays its formal execution status (`SUCCESS`, `VERIFICATION_WARNING`, `BLOCKED`) and consensus confidence score.
- **Telemetry Footer**: Displays the exact round-trip latency (ms) and peak VRAM allocated for each message.
- **Prompt Suggestion Chips**: Quick-start chips above the input box allow one-click testing of algebra, arithmetic, Python synthesis, composite tasks, and security guardrails.

### B. Live Neural Activity Panel (Right Drawer)
- Displays the real-time stage-by-stage pipeline for the latest query:
  1. **Reflex Screening & Security Guardrail**: Intercepts command injection and classifies query category.
  2. **Cognitive Planner**: Decomposes compound requests into sub-task DAGs.
  3. **Knowledge Retrieval**: Queries SQLite full-text search index for contextual documentation.
  4. **Specialist Neurons**: Displays output from `MathVerifierNeuron` (SymPy) or `CoderNeuron` (AST + Sandbox).
  5. **Consensus & Verification Engine**: Cross-checks confidence scores and detects logical contradictions.
- Displays exact duration (`duration_ms`) and execution state (`completed`, `blocked`, `warning`) for each stage.

### C. System Monitoring Dashboard
Auto-refreshes every 3 seconds:
- **GPU VRAM Consumption**: Real-time allocated VRAM vs. 3,500 MB headroom ceiling vs. 4,096 MB physical capacity.
- **Host System RAM**: Available memory in MB.
- **CPU Utilization %**: Background worker load.
- **Task Counters**: Total completed tasks, blocked threats, and failure counts.
- **Latency Tracking**: Average response latency and P95 latency.

### D. Model & Neuron Management
- **Neuron Fleet**: Inspect registered neurons, their specializations, total invocation counts, and average latencies.
- **Model Runner**: View currently loaded foundation model (`Qwen2.5-0.5B-Instruct` or `Qwen2.5-1.5B-Instruct`), active device (`cuda:0` / `cpu`), and quantization format.
- **Controls**: Load or unload model checkpoints dynamically with automatic VRAM cache purging.

---

## 3. REST API Documentation

The NEURON web server provides documented REST endpoints:

### `POST /api/chat`
Dispatches a prompt through the `NeuralCore` collective intelligence pipeline.
- **Request Body**:
  ```json
  {
    "prompt": "Evaluate the arithmetic expression: (145 * 28) - (3400 / 25) + 12",
    "session_id": "default"
  }
  ```
- **Response**:
  ```json
  {
    "task_id": "a1b2c3d4-...",
    "session_id": "default",
    "status": "SUCCESS",
    "category": "MATH",
    "consensus_score": 1.0,
    "total_latency_ms": 78.4,
    "response_markdown": "### Mathematical Verification (SymPy)\n...",
    "raw_results": { ... },
    "execution_timeline": [ ... ],
    "hardware_telemetry": { "peak_vram_mb": 26.0 }
  }
  ```

### `GET /api/telemetry`
Returns live hardware, task, and model metrics.
- **Response**:
  ```json
  {
    "gpu": {
      "device_name": "NVIDIA GeForce RTX 2050",
      "cuda_available": true,
      "allocated_vram_mb": 26.0,
      "usable_headroom_mb": 3474.0
    },
    "system": {
      "cpu_utilization_pct": 8.4,
      "free_ram_mb": 6240.0
    },
    "tasks": {
      "completed": 45,
      "blocked": 3,
      "failed": 0,
      "avg_latency_ms": 82.5,
      "p95_latency_ms": 135.0
    }
  }
  ```

### `GET /api/neurons`
Returns all registered micro-neurons and their operational statistics.

### `POST /api/model/load`
Loads a supported foundation model into memory.
- **Request Body**: `{"model": "qwen-0.5b", "force_cpu": false}`

### `POST /api/model/unload`
Releases model weights from GPU memory and purges CUDA cache.

---

## 4. Hardware Safety & VRAM Protection

The Chat UI connects directly to the `HardwareSupervisor`:
- If an operation requests memory that would breach the **500 MB safety buffer**, it is rejected or automatically routed to the CPU.
- Unloading a model triggers `torch.cuda.empty_cache()` and `gc.collect()`, recovering allocated VRAM to `0.00 MB`.
