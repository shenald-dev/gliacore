# GliaCore 0.3.0 — Comprehensive Testing & Quality Verification Guide

This document describes the multi-tier testing framework, execution instructions, quality gates, and verified test results for **GliaCore 0.3.0**.

---

## 1. Test Architecture Overview

Testing in GliaCore is divided into 5 independent tiers:

1. **Unit Tests:** Fast, isolated verification of individual classes (Hardware supervisor, Synapse bus, tools, neurons).
2. **Integration Tests:** Interaction between multiple subsystems (Router $\to$ Planner $\to$ Neurons $\to$ Verifier).
3. **End-to-End Workflow Tests:** Complete user workflows simulating REST API calls, server bootstrap, model lifecycle, and application restart.
4. **Stress & Stability Tests:** Workload scaling, thread concurrency, memory pressure, and fault injection.
5. **Security & Adversarial Tests:** Real-world penetration testing against command injection, sandbox escapes, and prompt jailbreaks.

---

## 2. Test Execution Commands

### Full Standard Test Suite (43 Tests):
```bash
python -m pytest -o pythonpath=src tests -v
```

### Full Test Suite with Code Coverage:
```bash
python -m pytest --cov=gliacore -o pythonpath=src tests
```

### End-to-End Workflow Tests (11 Workflows):
```bash
python -m pytest -o pythonpath=src tests/test_end_to_end_workflows.py -v
```

### Adversarial Security Penetration Suite:
```bash
python -m tests.security_adversarial_suite
```

### Extreme Stress & Fault Injection Suite:
```bash
python -m tests.stress_test_suite
```

---

## 3. Verified Test Summary (43/43 Passing, 100% Pass Rate)

| Test Module | Test Cases | Status | Key Verifications |
|---|---|---|---|
| `tests/test_end_to_end_workflows.py` | 11 | **PASSED** | REST API endpoints, chat workflows, model lifecycle, 4-tier memory, persistence across restart, document indexing, agent planning. |
| `tests/test_hardware.py` | 3 | **PASSED** | VRAM telemetry, memory tracer, 3,500 MB VRAM boundary enforcement. |
| `tests/test_neural_core.py` | 3 | **PASSED** | Math pipeline, code pipeline, security guardrail interception. |
| `tests/test_neurons.py` | 4 | **PASSED** | Reflex neuron classification, MathVerifier (SymPy), CoderNeuron (AST), Consensus engine. |
| `tests/test_phase3_advanced.py` | 9 | **PASSED** | Adaptive router difficulty, reasoning self-repair, memory hierarchy, NumPy engine, document indexer, autonomous agent, plugin manager, self-improvement. |
| `tests/test_rebranding_and_migration.py` | 5 | **PASSED** | Package metadata, `GliaCore` engine alias, `import neuron` backward-compatible stub & warning, environment variable fallback, database preservation. |
| `tests/test_synapse.py` | 3 | **PASSED** | MessagePack serialization round-trip, Pub/Sub event bus, point-to-point mailboxes. |
| `tests/test_tools.py` | 5 | **PASSED** | SymPy evaluation and equation solving, AST parser valid/syntax error, subprocess code sandbox. |

---

## 4. Code Coverage Breakdown

Measured on Python 3.11 with `pytest-cov`:

| Component Group | Statements | Misses | Statement Coverage |
|---|---|---|---|
| **Core Orchestration (`core/`)** | 371 | 51 | **86.3%** |
| **Specialist Neurons (`neurons/`)** | 187 | 50 | **73.3%** |
| **Reasoning & Reflection (`reasoning/`)** | 99 | 20 | **79.8%** |
| **Adaptive Router (`routing/`)** | 102 | 15 | **85.3%** |
| **Memory Hierarchy (`memory/`)** | 233 | 61 | **73.8%** |
| **Synapse Communication Bus (`synapse/`)** | 109 | 19 | **82.6%** |
| **Deterministic Tools (`tools/`)** | 262 | 88 | **66.4%** |
| **REST API Server (`ui/`)** | 212 | 47 | **77.8%** |
| **Overall Ecosystem Average** | **1,879** | **427** | **77.3%** |

---

## 5. Continuous Integration (CI)

GliaCore includes GitHub Actions workflows (`.github/workflows/ci.yml`) testing:
- Python 3.10 and Python 3.11
- Standard test suite execution
- Security penetration verification
- 3-Way architectural benchmark run
