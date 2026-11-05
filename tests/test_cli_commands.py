"""
Unit tests for GliaCore Command-Line Interface (CLI) Subcommands.
Tests version, tools, telemetry, and one-shot chat commands via subprocess.
"""

import sys
import subprocess


def test_cli_version():
    """Verify 'gliacore version' outputs correct version string."""
    res = subprocess.run(
        [sys.executable, "-m", "gliacore.ui.server", "version"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res.returncode == 0
    assert "GliaCore v0.4.0" in res.stdout


def test_cli_tools_listing():
    """Verify 'gliacore tools' prints registered tools."""
    res = subprocess.run(
        [sys.executable, "-m", "gliacore.ui.server", "tools"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res.returncode == 0
    assert "Registered GliaCore Tools" in res.stdout
    assert "math_solve" in res.stdout
    assert "datetime_now" in res.stdout


def test_cli_telemetry():
    """Verify 'gliacore telemetry' outputs hardware and latency information."""
    res = subprocess.run(
        [sys.executable, "-m", "gliacore.ui.server", "telemetry"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res.returncode == 0
    assert "GliaCore Hardware Telemetry" in res.stdout
    assert "VRAM Allocated" in res.stdout


def test_cli_one_shot_chat():
    """Verify 'gliacore chat <prompt>' processes task and outputs result."""
    res = subprocess.run(
        [sys.executable, "-m", "gliacore.ui.server", "chat", "Calculate 15 * 6"],
        capture_output=True,
        text=True,
        timeout=15
    )
    assert res.returncode == 0
    assert "Status: SUCCESS" in res.stdout
    assert "90" in res.stdout
