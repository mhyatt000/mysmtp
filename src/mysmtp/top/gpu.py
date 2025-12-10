import re

import os

def has_nvidia_gpu_dev():
    return any(os.path.exists(f"/dev/nvidia{i}") for i in range(16))


def parse_nvidia_smi(text: str):
    result = {
        "driver_version": None,
        "cuda_version": None,
        "gpus": [],
        "processes": []
    }

    lines = text.splitlines()

    # -----------------------------
    # Parse header for driver + CUDA
    # -----------------------------
    header_re = re.compile(r"NVIDIA-SMI\s+([\d\.]+).*CUDA Version:\s+([\d\.]+)")
    for line in lines:
        m = header_re.search(line)
        if m:
            result["driver_version"] = m.group(1)
            result["cuda_version"] = m.group(2)
            break

    # -----------------------------
    # Parse GPU summary blocks
    # -----------------------------
    gpu_section = False
    gpu_info_re = re.compile(
        r"\|\s*(\d+)\s+(.+?)\s+\S+\s*\|\s*([\w:]+)\s+(\S+)\s*\|.*"
    )
    metrics_re = re.compile(
        r"\|\s*\d+\s+(\d+)C.*?(\d+)W\s*/\s*(\d+)W\s*\|\s*(\d+)MiB\s*/\s*(\d+)MiB\s*\|\s*(\d+)%"
    )

    current_gpu = None

    for i, line in enumerate(lines):
        # Enter GPU blocks = look for "=== ..."
        if "===" in line and "GPU" in line:
            gpu_section = True
            continue

        if gpu_section:
            # GPU name + Bus ID line
            m1 = gpu_info_re.match(line)
            if m1:
                gpu_index = int(m1.group(1))
                name = m1.group(2).strip()
                bus_id = m1.group(3)
                current_gpu = {
                    "index": gpu_index,
                    "name": name,
                    "bus_id": bus_id,
                    "temperature_C": None,
                    "power_usage_W": None,
                    "power_cap_W": None,
                    "memory_used_MiB": None,
                    "memory_total_MiB": None,
                    "util_percent": None
                }
                continue

            # Metrics line directly under the GPU info
            m2 = metrics_re.match(line)
            if m2 and current_gpu is not None:
                current_gpu["temperature_C"] = int(m2.group(1))
                current_gpu["power_usage_W"] = int(m2.group(2))
                current_gpu["power_cap_W"] = int(m2.group(3))
                current_gpu["memory_used_MiB"] = int(m2.group(4))
                current_gpu["memory_total_MiB"] = int(m2.group(5))
                current_gpu["util_percent"] = int(m2.group(6))
                result["gpus"].append(current_gpu)
                current_gpu = None

        # Exit GPU section when process table begins
        if "Processes:" in line:
            gpu_section = False
            break

    # -----------------------------
    # Parse Process Table
    # -----------------------------
    process_line_re = re.compile(
        r"\|\s*(\d+)\s+N/A\s+N/A\s+(\d+)\s+(\w)\s+(.+?)\s+(\d+)MiB"
    )

    in_proc = False
    for line in lines:
        if "Processes:" in line:
            in_proc = True
            continue
        if in_proc:
            m = process_line_re.match(line)
            if m:
                gpu_idx = int(m.group(1))
                pid = int(m.group(2))
                ptype = m.group(3)
                procname = m.group(4).strip()
                mem = int(m.group(5))
                result["processes"].append({
                    "gpu": gpu_idx,
                    "pid": pid,
                    "type": ptype,    # C = compute, G = graphics
                    "process_name": procname,
                    "gpu_memory_MiB": mem
                })

    return result

