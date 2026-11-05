# GliaCore 0.3.0 — User Guide & Manual

Welcome to **GliaCore 0.3.0**, an edge-optimized micro-AI collective intelligence platform. This guide explains how to use GliaCore effectively through both the interactive **GliaCore Studio** web dashboard and the Python SDK.

---

## 1. Getting Started: Launching GliaCore Studio

Start the local server from your terminal:
```bash
gliacore
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

You will see **GliaCore Studio** with the 6 dedicated workspaces:

1. **Workspace 1: Chat & Execution Timeline** (Primary reasoning interface)
2. **Workspace 2: Memory Explorer** (Inspect and manage 4-tier knowledge)
3. **Workspace 3: Autonomous Agent** (Goal decomposition and execution)
4. **Workspace 4: Knowledge Ingestion** (Index local documents for RAG)
5. **Workspace 5: Telemetry & Optimizer** (Live GPU/VRAM meters and self-improvement)
6. **Workspace 6: Neuron Fleet** (Inspect specialist neurons and model status)

---

## 2. Using Workspace 1: Interactive Chat

The chat workspace allows you to submit natural language prompts across several intelligence domains:

### A. Mathematical Problem Solving
Type an arithmetic or algebraic question:
> *"Calculate 145 * 28 + 3600 / 15"*  
> *"Solve the equation: 5*x - 35 = 65"*

**What happens:**
1. The **Adaptive Router** classifies the task as `MATH`.
2. The task is routed to the **Math Verifier Neuron**, which uses the deterministic **SymPy** symbolic engine.
3. The response displays the exact result, the verified symbolic steps, and sub-millisecond execution telemetry.

### B. Code Synthesis & Verification
Type a coding request:
> *"Write a Python function to compute the greatest common divisor of two integers."*

**What happens:**
1. The **Coder Neuron** synthesizes the Python code.
2. The **AST Parser Tool** analyzes the syntax tree to ensure validity.
3. The **Advanced Reasoning Engine** verifies execution inside a sandboxed subprocess.
4. The output shows the formatted Python code, syntax status, and execution output.

### C. Security Guardrail Demonstration
Try typing a potentially destructive shell command:
> *"rm -rf / --no-preserve-root"*

**What happens:**
1. The **Reflex Neuron** immediately intercepts the pattern in $<0.2$ ms.
2. The request is safely blocked with a red execution card explaining the safety violation.
3. No subprocess or model execution occurs.

---

## 3. Using Workspace 2: 4-Tier Memory Hierarchy

GliaCore separates memory into 4 distinct biological tiers:

1. **Working Memory:** Transient scratchpad for intermediate calculation artifacts during an active session.
2. **Episodic Memory:** Records past successful solutions and problem contexts.
3. **Semantic Memory:** Curated, verified knowledge facts.
4. **Procedural Memory:** Executable workflows and tool recipes.

### Managing Memories:
- In the **Memory Explorer**, filter by tier (`All`, `Working`, `Episodic`, `Semantic`, `Procedural`).
- View the reliability score ($0.0$ to $1.0$) and access frequency.
- Click **Delete** on any memory item to permanently prune it from the SQLite database.

---

## 4. Using Workspace 3: Autonomous Agent

For goals requiring multiple steps:
1. Navigate to the **Autonomous Agent** tab.
2. Enter a high-level goal, e.g.:
   > *"Audit security vulnerabilities in directory src/gliacore"*
3. Click **Generate Plan**. The agent constructs a Directed Acyclic Graph (DAG) with discrete execution steps.
4. Click **Step Execution** to step through each sub-task sequentially, or **Cancel Task** to immediately halt execution.

---

## 5. Using Workspace 4: Document Ingestion & Citations

1. Place local markdown or text files in your project directory.
2. Enter the file path in the Document Ingestion workspace and click **Ingest**.
3. GliaCore chunks the document and stores it in SQLite with Full-Text Search (FTS).
4. Query the index to view extracted text snippets and citation sources.

---

## 6. Using Workspace 5: Hardware Telemetry

GliaCore displays live telemetry for your system:
- **GPU VRAM Allocation Gauge:** Shows current allocated VRAM vs. the 3,500 MB safe usable boundary.
- **System RAM Free:** Real-time host memory availability.
- **Router Decisions:** Breakdown of tasks routed to `SIMPLE`, `MODERATE`, and `COMPLEX` pipelines.
- **Self-Improvement Proposals:** Automated recommendations detected by the self-improvement engine.

---

## 7. Python SDK Integration

To use GliaCore directly inside your Python applications:

```python
from gliacore.core.engine import GliaCore

# Initialize the orchestrator
core = GliaCore()

# Execute a reasoning task
result = core.process("Solve 3*x^2 - 12 = 0")

print(f"Status: {result['status']}")
print(f"Solutions: {result['results']['math']['result']['solutions']}")

# Close database connections on shutdown
core.close()
```
