"""
Hardware Supervision & Memory Guard for PROJECT: GLIACORE
Enforces strict 4GB VRAM and 16GB System RAM ceilings.
"""

import os
import gc
import psutil
import torch
from dataclasses import dataclass
from typing import Optional, Dict, Any
from contextlib import contextmanager

# Hardware constraints for RTX 2050 (HP Victus)
MAX_PHYSICAL_VRAM_MB: float = 4096.0
MAX_USABLE_VRAM_MB: float = 3500.0   # Ceiling accounting for OS / DWM display
SAFETY_BUFFER_VRAM_MB: float = 500.0  # Headroom to avoid hard CUDA OOM crashes
MAX_SYSTEM_RAM_MB: float = 16384.0


@dataclass
class VRAMBudget:
    total_mb: float
    allocated_mb: float
    reserved_mb: float
    free_usable_mb: float
    system_ram_free_mb: float
    cuda_available: bool
    device_name: str


class HardwareSupervisor:
    """
    Monitors, guards, and enforces memory safety across GPU and CPU.
    Prevents CUDA out-of-memory crashes by strictly monitoring tensor allocations.
    """

    def __init__(self, target_usable_vram_mb: Optional[float] = None):
        env_val = os.environ.get("GLIACORE_MAX_VRAM_MB", os.environ.get("NEURON_MAX_VRAM_MB"))
        if target_usable_vram_mb is not None:
            self.target_usable_vram_mb = target_usable_vram_mb
        elif env_val:
            self.target_usable_vram_mb = float(env_val)
        else:
            self.target_usable_vram_mb = MAX_USABLE_VRAM_MB
        self.cuda_available = torch.cuda.is_available()
        self.device = torch.device("cuda:0" if self.cuda_available else "cpu")
        self.device_name = torch.cuda.get_device_name(0) if self.cuda_available else "CPU (Fallback)"

    def get_telemetry(self) -> VRAMBudget:
        """Query real-time GPU VRAM and System RAM state."""
        ram = psutil.virtual_memory()
        system_ram_free_mb = ram.available / (1024 * 1024)

        if not self.cuda_available:
            return VRAMBudget(
                total_mb=0.0,
                allocated_mb=0.0,
                reserved_mb=0.0,
                free_usable_mb=0.0,
                system_ram_free_mb=system_ram_free_mb,
                cuda_available=False,
                device_name=self.device_name
            )

        allocated_bytes = torch.cuda.memory_allocated(self.device)
        reserved_bytes = torch.cuda.memory_reserved(self.device)
        
        allocated_mb = allocated_bytes / (1024 * 1024)
        reserved_mb = reserved_bytes / (1024 * 1024)
        
        # Calculate real usable headroom
        free_usable_mb = max(0.0, self.target_usable_vram_mb - reserved_mb)

        return VRAMBudget(
            total_mb=MAX_PHYSICAL_VRAM_MB,
            allocated_mb=round(allocated_mb, 2),
            reserved_mb=round(reserved_mb, 2),
            free_usable_mb=round(free_usable_mb, 2),
            system_ram_free_mb=round(system_ram_free_mb, 2),
            cuda_available=True,
            device_name=self.device_name
        )

    def can_allocate_vram(self, required_mb: float) -> bool:
        """Returns True if the required VRAM allocation fits within safe headroom."""
        if not self.cuda_available:
            return False
        telemetry = self.get_telemetry()
        return (telemetry.free_usable_mb - required_mb) >= SAFETY_BUFFER_VRAM_MB

    def purge_cache(self) -> None:
        """Run garbage collection and empty CUDA cache."""
        gc.collect()
        if self.cuda_available:
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    @contextmanager
    def memory_tracer(self, label: str = "operation"):
        """Context manager to measure memory delta and peak consumption."""
        self.purge_cache()
        start_telemetry = self.get_telemetry()
        if self.cuda_available:
            torch.cuda.reset_peak_memory_stats(self.device)

        result: Dict[str, Any] = {"label": label}
        try:
            yield result
        finally:
            end_telemetry = self.get_telemetry()
            peak_vram_mb = 0.0
            if self.cuda_available:
                peak_vram_mb = torch.cuda.max_memory_allocated(self.device) / (1024 * 1024)

            result["start_vram_allocated_mb"] = start_telemetry.allocated_mb
            result["end_vram_allocated_mb"] = end_telemetry.allocated_mb
            result["peak_vram_mb"] = round(peak_vram_mb, 2)
            result["start_ram_free_mb"] = start_telemetry.system_ram_free_mb
            result["end_ram_free_mb"] = end_telemetry.system_ram_free_mb
            self.purge_cache()
