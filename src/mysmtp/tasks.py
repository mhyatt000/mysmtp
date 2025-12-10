from pathlib import Path
import subprocess

import pandas as pd

from mysmtp.top.gpu import has_nvidia_gpu_dev, parse_nvidia_smi


def log_gpu_metrics() -> None:
    """Collect GPU metrics via ``nvidia-smi`` and append them to CSV files.

    The function exits early when no NVIDIA GPU devices are present or when
    ``nvidia-smi`` cannot be executed.
    """
    if not has_nvidia_gpu_dev():
        return

    try:
        result = subprocess.run(
            ["nvidia-smi"], capture_output=True, text=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return

    parsed = parse_nvidia_smi(result.stdout)
    timestamp = pd.Timestamp.utcnow()

    gpu_rows = []
    for gpu in parsed.get("gpus", []):
        gpu_rows.append(
            {
                "timestamp": timestamp,
                "driver_version": parsed.get("driver_version"),
                "cuda_version": parsed.get("cuda_version"),
                "index": gpu.get("index"),
                "name": gpu.get("name"),
                "bus_id": gpu.get("bus_id"),
                "temperature_C": gpu.get("temperature_C"),
                "power_usage_W": gpu.get("power_usage_W"),
                "power_cap_W": gpu.get("power_cap_W"),
                "memory_used_MiB": gpu.get("memory_used_MiB"),
                "memory_total_MiB": gpu.get("memory_total_MiB"),
                "util_percent": gpu.get("util_percent"),
            }
        )

    if gpu_rows:
        gpu_df = pd.DataFrame(gpu_rows)
        gpu_path = Path("gpu_metrics.csv")
        gpu_df.to_csv(gpu_path, mode="a", header=not gpu_path.exists(), index=False)

    process_rows = []
    for proc in parsed.get("processes", []):
        process_rows.append({"timestamp": timestamp, **proc})

    if process_rows:
        proc_df = pd.DataFrame(process_rows)
        proc_path = Path("gpu_processes.csv")
        proc_df.to_csv(proc_path, mode="a", header=not proc_path.exists(), index=False)
