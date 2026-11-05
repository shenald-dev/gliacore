# Contributing to GliaCore

Thank you for your interest in contributing to **GliaCore**! We welcome bug reports, documentation improvements, new specialist neurons, deterministic tools, and architecture enhancements.

---

## 1. Code of Conduct

We are committed to providing an open, welcoming, and harassment-free community. Please treat all contributors with respect and professionalism.

---

## 2. Development Workflow

### Step 1: Fork and Clone
```bash
git clone https://github.com/your-username/gliacore.git
cd gliacore
```

### Step 2: Set Up Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -e ".[dev]"
```

### Step 3: Create a Feature Branch
```bash
git checkout -b feature/my-new-neuron
```

### Step 4: Implement & Test
Make your changes following our coding principles:
- Maintain deterministic precedence (prefer symbolic/AST tools over probabilistic LLM prompts).
- Never exceed the 3,500 MB VRAM ceiling for 4GB consumer GPUs.
- All code must pass existing tests and include new test cases.

```bash
# Verify all tests pass
python -m pytest -o pythonpath=src tests -v

# Run linter
ruff check src tests
```

### Step 5: Submit a Pull Request
- Provide a clear, detailed PR description.
- Reference any relevant issues.
- Ensure GitHub Actions CI passes.

---

## 3. Licensing Notice

By contributing to GliaCore, you agree that your contributions will be licensed under the **GNU General Public License v3.0 (GPLv3)**.
