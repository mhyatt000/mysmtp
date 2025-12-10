import psutil
import shutil

def get_system_stats():
    stats = {}

    # --------------------
    # MEMORY
    # --------------------
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()

    stats["memory"] = {
        "total": vm.total,
        "used": vm.used,
        "free": vm.free,
        "available": vm.available,
        "cached": vm.cached if hasattr(vm, "cached") else None,
        "percent": vm.percent,
    }

    stats["swap"] = {
        "total": sm.total,
        "used": sm.used,
        "free": sm.free,
        "percent": sm.percent,
    }

    # --------------------
    # DISK USAGE PER MOUNT
    # --------------------
    disk_info = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue

        disk_info[part.mountpoint] = {
            "device": part.device,
            "fstype": part.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
        }

    stats["disks"] = disk_info

    # --------------------
    # DISK IO COUNTERS (GLOBAL AND PER-DISK)
    # --------------------
    io_global = psutil.disk_io_counters()
    stats["disk_io_global"] = {
        "read_bytes": io_global.read_bytes,
        "write_bytes": io_global.write_bytes,
        "read_count": io_global.read_count,
        "write_count": io_global.write_count,
    }

    stats["disk_io_perdisk"] = {}
    per_disk = psutil.disk_io_counters(perdisk=True)
    for disk, io in per_disk.items():
        stats["disk_io_perdisk"][disk] = {
            "read_bytes": io.read_bytes,
            "write_bytes": io.write_bytes,
            "read_count": io.read_count,
            "write_count": io.write_count,
        }

    return stats

