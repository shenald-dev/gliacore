# GliaCore Changelog

All notable changes to **GliaCore** (formerly PROJECT: NEURON) are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
