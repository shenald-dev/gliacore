"""
Unit tests for Hardware Supervisor & VRAM Budget
"""

import torch
from gliacore.core.hardware import HardwareSupervisor


def test_hardware_supervisor_telemetry():
    supervisor = HardwareSupervisor()
    telemetry = supervisor.get_telemetry()

    assert telemetry.total_mb >= 0.0
    assert telemetry.system_ram_free_mb > 0.0
    assert isinstance(telemetry.cuda_available, bool)
    assert isinstance(telemetry.device_name, str)


def test_hardware_memory_tracer():
    supervisor = HardwareSupervisor()
    with supervisor.memory_tracer(label="test_tensor_op") as stats:
        # Allocate a small tensor to verify tracking
        if supervisor.cuda_available:
            t = torch.ones((512, 512), device="cuda")
            _ = t * 2.0
        else:
            t = torch.ones((512, 512))
            _ = t * 2.0

    assert "start_vram_allocated_mb" in stats
    assert "end_vram_allocated_mb" in stats
    assert "peak_vram_mb" in stats
    assert stats["label"] == "test_tensor_op"


def test_can_allocate_vram_boundary():
    supervisor = HardwareSupervisor()
    if supervisor.cuda_available:
        # Should be able to allocate tiny 1MB
        assert supervisor.can_allocate_vram(1.0) is True
        # Should reject absurdly huge 100,000MB allocation
        assert supervisor.can_allocate_vram(100000.0) is False
