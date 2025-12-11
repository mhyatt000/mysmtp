"""Disk usage logging helpers."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from ..top.disk import get_system_stats


def _prepare_disk_rows(stats: dict) -> list[dict]:
    """Transform disk stats into a tabular structure.

    Parameters
    ----------
    stats:
        System statistics dictionary produced by :func:`get_system_stats`.
    """

    disks: dict[str, dict] = stats.get("disks", {})
    rows: list[dict[str, object]] = []
    timestamp = datetime.now().isoformat()

    for mountpoint, info in disks.items():
        rows.append(
            {
                "timestamp": timestamp,
                "mountpoint": mountpoint,
                "device": info.get("device"),
                "fstype": info.get("fstype"),
                "total": info.get("total"),
                "used": info.get("used"),
                "free": info.get("free"),
                "percent": info.get("percent"),
            }
        )

    return rows


def log_disk_usage(csv_path: str | Path = "du.csv") -> Path:
    """Record current disk usage metrics to a CSV file.

    The data is gathered via :mod:`psutil` using the :mod:`mysmtp.top.disk`
    helper, converted to a :class:`pandas.DataFrame`, and appended to a CSV
    file. If the file does not exist, the header is written automatically.

    Parameters
    ----------
    csv_path:
        Destination CSV filename. Defaults to ``"du.csv"`` in the working
        directory.

    Returns
    -------
    :class:`pathlib.Path`
        Path to the written CSV file.
    """

    stats = get_system_stats()
    rows = _prepare_disk_rows(stats)
    df = pd.DataFrame(rows)

    csv_path = Path(csv_path)
    header = not csv_path.exists()
    df.to_csv(csv_path, mode="a" if not header else "w", header=header, index=False)

    return csv_path
