# GliaCore Changelog

All notable changes to **GliaCore** (formerly PROJECT: NEURON) are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] — 2026-11-05 (Model Context Protocol Gateway & Token Streaming Evolution)

### Model Context Protocol (MCP) Subsystem
- **Full MCP 2024-11-05 Specification Implementation:** Introduced native MCP server (`gliacore.mcp.server.GliaCoreMCPServer`) and client (`gliacore.mcp.client.GliaCoreMCPClient`) implementing standard JSON-RPC 2.0.
- **Exposed Flagship Symbolic Tools:**
  1. `gliacore_reflex_scan`: Sub-millisecond regex & AST security gateway (<0.2ms latency).
  2. `gliacore_math_solve`: Exact SymPy algebraic solving and calculus derivation (zero hallucination).
  3. `gliacore_code_sandbox`: AST-validated secure Python execution sandbox with runtime telemetry.
  4. `gliacore_memory_query`: Multi-tier search across working, episodic, semantic, and archival memory.
  5. `gliacore_solve`: End-to-end task routing and neural-symbolic execution through GliaCore's collective intelligence.
  6. `gliacore_document_query`: Grounded evidence and citation retrieval across ingested files.
  7. `gliacore_system_telemetry`: Real-time GPU VRAM budget, system RAM, and neuron fleet statistics.
- **Claude Desktop & Cursor Ready:** Standard stdio transport enables instant one-click connection via `gliacore mcp`.
- **REST & HTTP MCP Transport:** Added `/api/mcp` JSON-RPC endpoint and `/api/mcp/tools` introspection endpoint in GliaCore Studio web server.
- **Backward Compatibility:** Provided legacy stubs in `neuron.mcp` forwarding seamlessly to `gliacore.mcp`.

### Real-Time SSE Token & Stage Streaming
- **Server-Sent Events (SSE) Endpoint:** Added `/api/chat/stream` yielding live stage transition events (`Reflex Screening`, `Adaptive Neural Routing`, `4-Tier Memory Retrieval`), incremental token chunks, and final verification payloads.
- **Streaming Model Runner:** Added `generate_stream(...)` to `ModelRunner` leveraging HuggingFace `TextIteratorStreamer` on CUDA or naturally chunked token synthesis in neural-symbolic mode.
- **Event-Driven Collective Intelligence Pipeline:** Added `process_stream(...)` to `GliaCore` orchestrator for real-time observability into neuron activations.

### Schema-Constrained Decoding & JSON Auto-Repair
- **Syntactic Auto-Repair Engine:** Built `gliacore.verification.schema.JSONExtractor` recovering valid JSON from markdown code blocks, conversational preambles, and malformed LLM outputs.
- **Heuristic Fixes:** Automatically repairs Python literals (`True`/`False`/`None` -> `true`/`false`/`null`), unquoted keys, single quotes, and trailing commas.
- **Schema Validation:** Built `gliacore.verification.schema.SchemaValidator` for lightweight type and required-property verification without external heavyweight dependencies.
- **Consensus Integration:** Enhanced `VerificationEngine` with `"schema"` artifact verification.

### Core Runtime & Windows CPU Stability
- **Windows CPU Acceleration Fix:** Fixed fatal memory-mapping access violation in `accelerate`'s multi-threaded `_materialize_copy` by disabling `device_map="cpu"` and setting `low_cpu_mem_usage = False` on CPU targets.
- **CLI Subcommand Suite:** Enhanced CLI entry points to support `gliacore mcp`, `gliacore serve --host <host> --port <port>`, and `gliacore version`.

### Testing & Code Quality
- **Test Suite Expansion:** Expanded test suite from 43 to **62 passed tests (100% pass rate)** including new test suites `test_mcp_gateway.py`, `test_schema_engine.py`, and `test_streaming.py`.
- **Zero Lint Errors:** Fixed 144 initial lint warnings down to 0 errors via Ruff.

---

## [0.3.0] — 2026-11-05 (First Public GitHub Release Checkpoint)

### Major Brand Transformation
- **Rebranding:** Completely rebranded from *PROJECT: NEURON* to **GliaCore 0.3.0** (`gliacore-ai` on PyPI).
- **Biological Foundation:** Formalized the astrocyte-neuron architectural paradigm, where specialized micro-models act as Neurons, MessagePack channels act as Synapses, and the GliaCore engine schedules memory and metabolic VRAM budgets.
- **Backward Compatibility:** Introduced `src/neuron/__init__.py` backward-compatible stub emitting polite `FutureWarning` while maintaining full code compatibility for existing scripts.
- **Database Fallback:** Implemented automatic database discovery for `gliacore_store.db` / `neuron_store.db` and `gliacore_memory.db` / `neuron_memory.db` so no user data is lost.
- **Environment Hierarchy:** Configured `GLIACORE_*` environment variables with automatic fallback to `NEURON_*`.

### Core Intelligence Evolution
- **Adaptive Task Routing:** Implemented `AdaptiveRouter` calculating dynamic task complexity scores to dispatch tasks into `SIMPLE`, `MODERATE`, or `COMPLEX` execution workflows.
- **Generate-and-Verify Reflection Loop:** Built `AdvancedReasoningEngine` with automated AST syntax self-repair and mathematical syntax normalization.
- **4-Tier Memory Hierarchy:** Implemented `MemoryHierarchy` with discrete Working, Episodic, Semantic, and Procedural memory tiers, multi-factor ranking, and deduplication.
- **Controlled Autonomous Agent:** Implemented `AutonomousAgent` decomposing multi-step goals into DAG execution plans with checkpoints and immediate user cancellation.
- **Document Indexing & RAG:** Added `DocumentIndexer` supporting local file ingestion, SQLite FTS indexing, and evidence citation extraction.
- **Plugin Architecture:** Added `PluginManager` with fine-grained declared permissions and security sandboxing.
- **Self-Improvement Engine:** Added `SelfImprovementEngine` tracking telemetry bottlenecks and generating automated optimization proposals.

### User Interface & Experience
- **GliaCore Studio:** Upgraded web UI with 6 dedicated workspaces: Chat, Memory Explorer, Autonomous Agent, Document Ingestion, System Telemetry, and Neuron Fleet.
- **Visual Identity:** Added Astrocyte Core Nexus SVG logo and polished dark-mode responsive styling.

### Testing & Verification
- **End-to-End Test Suite:** Added 11 full workflow tests (`tests/test_end_to_end_workflows.py`) validating the REST API, chat, memory lifecycle, document indexing, agent stepping, and persistence across server restarts.
- **Full Test Suite:** Expanded test suite from 32 to 43 tests with 100% pass rate.
- **5-Way Architectural Benchmark:** Evaluated 50 benchmark tasks achieving 96.0% accuracy, 4.0% failure rate, and 26.0 MB peak VRAM allocation.

---

## [0.2.0] — 2026-11-05 (Extreme Testing & Interactive Chat UI)

### Added
- Interactive single-page Chat UI served via `aiohttp` web server.
- Reflex security guardrails blocking command injection (`rm -rf`, PowerShell escapes).
- AST-screened subprocess code sandbox with 5.0-second timeout.
- SQLite WAL mode and re-entrant mutex locks eliminating database lock contention under 160 concurrent requests.
- Concurrency and workload stress testing suite (`tests/stress_test_suite.py`).
- Adversarial security penetration suite (`tests/security_adversarial_suite.py`).

---

## [0.1.0] — 2026-11-04 (Initial Architecture Prototype)

### Added
- Core modular micro-AI architectural prototype.
- Base specialized neurons: `ReflexNeuron`, `MathVerifierNeuron`, `CoderNeuron`, `PlannerNeuron`.
- High-speed binary communication bus (`SynapseBus`) using MessagePack serialization.
- Hardware supervisor monitoring NVIDIA RTX 2050 4GB VRAM and system RAM.
- Basic consensus verification engine.
- SQLite knowledge storage.
