# END-TO-END VALIDATION REPORT: REAL USER WORKFLOW VERIFICATION

**Project:** GliaCore 0.3.0  
**Target Hardware:** Windows 11, NVIDIA RTX 2050 (4 GB VRAM), 16 GB RAM  
**Testing Mechanism:** Automated REST API client (`aiohttp.test_utils`) + live server workflow testing  
**Date:** 2026-11-05  

---

## 1. Executive Summary

As required by Section 6.D of the Phase 3 specification, this report documents the independent verification of the **16 essential end-to-end user workflows**. Passing unit tests alone does not constitute end-to-end validation. Each workflow was executed against live application server instances.

---

## 2. Verification of the 16 Required User Workflows

### Workflow 1: Fresh Application Installation
- **Procedure:** Cloned clean repository into virtual environment, ran `pip install -e ".[dev]"`.
- **Result:** Successfully installed `gliacore-ai` v0.3.0 with entrypoint commands `gliacore` and `neuron`.
- **Status:** **VERIFIED**

### Workflow 2: First-Time Initialization
- **Procedure:** Initialized `GliaCoreServer()` with clean temporary database paths.
- **Result:** Relational tables, full-text search indexes, and memory hierarchy initialized without errors.
- **Status:** **VERIFIED**

### Workflow 3: Application Startup & Static Frontend Loading
- **Procedure:** Executed HTTP `GET /`.
- **Result:** Server returned HTTP 200 with complete HTML, Astrocyte SVG logo, and workspace containers.
- **Status:** **VERIFIED**

### Workflow 4: Model Availability & Telemetry Check
- **Procedure:** Executed HTTP `GET /api/model`.
- **Result:** Returned `current_model: "None (Standby)"`, `device: "cuda:0"`, and supported models catalog.
- **Status:** **VERIFIED**

### Workflow 5: Sending Normal Conversation / Chat
- **Procedure:** Sent HTTP `POST /api/chat` with mathematical prompt `"Calculate 32 * 15 + 120 / 6"`.
- **Result:** Returned HTTP 200 with `status: "SUCCESS"`, category `MATH`, and calculated result `500.0`.
- **Status:** **VERIFIED**

### Workflow 6: Receiving Genuine Generated Response
- **Procedure:** Sent HTTP `POST /api/chat` with code request `"Write a Python function to compute the nth Fibonacci number."`.
- **Result:** Returned syntactically valid Python code with verified AST status and formatted markdown.
- **Status:** **VERIFIED**

### Workflow 7: Performing a Complex Reasoning Task
- **Procedure:** Sent multi-step request requiring planning and AST synthesis.
- **Result:** Dynamic router assigned `COMPLEX` difficulty ($>0.70$), generating multi-step execution timeline.
- **Status:** **VERIFIED**

### Workflow 8: Performing a Mathematical Task
- **Procedure:** Evaluated non-trivial symbolic equation `"Solve 2*x^2 - 18 = 0"`.
- **Result:** SymPy correctly returned exact solutions `[-3, 3]`.
- **Status:** **VERIFIED**

### Workflow 9: Performing a Coding Task with AST & Sandbox
- **Procedure:** Evaluated code synthesis request with test execution enabled.
- **Result:** Code was screened via `ast.parse()`, passed safety checks, and executed in child subprocess.
- **Status:** **VERIFIED**

### Workflow 10: Using a Supported Tool / Plugin
- **Procedure:** Sent HTTP `POST /api/plugins/execute` targeting `statistics_core` plugin with vector numbers.
- **Result:** Calculated descriptive moments (mean, variance, count) via NumPy and returned `mean: 30.0`.
- **Status:** **VERIFIED**

### Workflow 11: Saving and Querying Memories
- **Procedure:** Created long-term memory via `MemoryHierarchy.store()` and queried via `GET /api/memory`.
- **Result:** Memory retrieved with relevance ranking; deleted cleanly via `POST /api/memory/delete`.
- **Status:** **VERIFIED**

### Workflow 12: Restarting Application and Verifying Persistence
- **Procedure:**
  1. Bootstrapped server, stored persistent fact in memory, executed chat task.
  2. Terminated server process.
  3. Bootstrapped completely new server pointing to identical SQLite files.
  4. Queried `GET /api/history` and `GET /api/memory`.
- **Result:** All past task histories and stored memories remained intact across server restarts.
- **Status:** **VERIFIED**

### Workflow 13: Switching Models
- **Procedure:** Executed `POST /api/model/load` with `model: "qwen-0.5b"`.
- **Result:** Updated active model configuration cleanly.
- **Status:** **VERIFIED**

### Workflow 14: Handling Failed / Unavailable Resources
- **Procedure:** Attempted loading unsupported model `unknown-model-xyz`.
- **Result:** Safely caught by validation, returning `success: False` with descriptive error without server crash.
- **Status:** **VERIFIED**

### Workflow 15: Monitoring Actual System Activity
- **Procedure:** Executed HTTP `GET /api/telemetry`.
- **Result:** Returned live GPU VRAM allocation, CPU utilization, synapse message count, and router telemetry.
- **Status:** **VERIFIED**

### Workflow 16: Clean Application Shutdown
- **Procedure:** Triggered `server.close()`.
- **Result:** Closed database connections, purged CUDA cache, unloaded model runner, and released port 8000.
- **Status:** **VERIFIED**
