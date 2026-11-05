"""
Rebranding and Backward Compatibility Verification Test Suite
Validates:
1. Native GliaCore 0.3.0 namespace and primary interfaces
2. Backward-compatible 'import neuron' stub and deprecation warnings
3. Automatic database discovery and fallback preservation
4. Environment variable priority (GLIACORE_* with fallback to NEURON_*)
"""

import sqlite3
import pytest


def test_gliacore_package_metadata():
    import gliacore
    assert gliacore.__version__ == "0.4.0"
    assert "GliaCore" in gliacore.__all__
    assert "NeuralCore" in gliacore.__all__
    assert "HardwareSupervisor" in gliacore.__all__


def test_gliacore_engine_alias_and_execution():
    from gliacore.core.engine import GliaCore, NeuralCore

    # Both GliaCore and NeuralCore refer to the orchestrator
    assert GliaCore is NeuralCore

    core = GliaCore(db_path=":memory:", memory_db_path=":memory:")
    res = core.process("Calculate 25 * 14 + 180 / 4")
    assert res["status"] == "SUCCESS"
    assert res["category"] == "MATH"
    assert "math" in res["results"]
    assert res["results"]["math"]["result"]["numeric"] == 395.0
    core.close()


def test_legacy_neuron_backward_compatibility():
    import sys
    if "neuron" in sys.modules:
        del sys.modules["neuron"]
    with pytest.warns(FutureWarning, match="The 'neuron' package namespace is deprecated"):
        import neuron

    assert hasattr(neuron, "GliaCore")
    assert hasattr(neuron, "NeuralCore")
    assert hasattr(neuron, "HardwareSupervisor")
    assert neuron.__version__ == "0.4.0"


def test_hardware_supervisor_environment_variable_hierarchy(monkeypatch):
    from gliacore.core.hardware import HardwareSupervisor

    # Test GLIACORE_MAX_VRAM_MB priority
    monkeypatch.setenv("GLIACORE_MAX_VRAM_MB", "2800.0")
    monkeypatch.setenv("NEURON_MAX_VRAM_MB", "3200.0")
    hw = HardwareSupervisor()
    assert hw.target_usable_vram_mb == 2800.0

    # Test fallback to NEURON_MAX_VRAM_MB when GLIACORE_* is unset
    monkeypatch.delenv("GLIACORE_MAX_VRAM_MB")
    hw_fallback = HardwareSupervisor()
    assert hw_fallback.target_usable_vram_mb == 3200.0


def test_database_discovery_and_data_preservation(tmp_path, monkeypatch):
    from gliacore.core.engine import GliaCore

    monkeypatch.chdir(tmp_path)

    # 1. When neither DB exists, creates gliacore_*.db
    core1 = GliaCore()
    assert "gliacore_store.db" in str(core1.storage.db_path)
    core1.close()

    # 2. When legacy neuron_store.db exists as a valid SQLite DB, GliaCore automatically binds to it
    legacy_db = tmp_path / "neuron_store.db"
    conn = sqlite3.connect(legacy_db)
    conn.execute("CREATE TABLE dummy (id INTEGER PRIMARY KEY)")
    conn.close()

    # Remove any gliacore_store.db in this temp folder
    g_db = tmp_path / "gliacore_store.db"
    if g_db.exists():
        g_db.unlink()

    core2 = GliaCore()
    assert "neuron_store.db" in str(core2.storage.db_path)
    core2.close()
