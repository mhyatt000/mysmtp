"""Plot GPU metrics from a csv file.

This module focuses on plotting total GPU utilization and memory
utilization for the current day. It expects a timestamp column and
percentage columns for GPU utilization and GPU memory utilization.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# Candidate column names to keep the loader flexible
TIMESTAMP_COLUMNS: Tuple[str, ...] = ("timestamp", "time", "datetime")
UTIL_COLUMNS: Tuple[str, ...] = (
    "gpu_util_percent",
    "gpu_util_pct",
    "util_percent",
    "util_pct",
    "gpu_util",
)
MEM_COLUMNS: Tuple[str, ...] = (
    "gpu_mem_percent",
    "gpu_mem_pct",
    "mem_percent",
    "mem_pct",
    "memory_util_percent",
    "memory_util_pct",
)


def _pick_column(df: pd.DataFrame, candidates: Iterable[str], label: str) -> str:
    for col in candidates:
        if col in df.columns:
            return col
    raise KeyError(f"CSV must include a {label} column (tried: {', '.join(candidates)}).")


def plot_gpu_day(csv_path: str | Path):
    """Load ``gpu.csv`` and plot GPU utilization for the current day.

    The plot shows GPU utilization (bars) and GPU memory utilization
    (line) over the course of the current day. The function filters rows
    to the current date based on the timestamp column.

    Parameters
    ----------
    csv_path:
        Path to the ``gpu.csv`` file. The CSV must include a timestamp
        column and percentage columns for GPU utilization and memory
        utilization.

    Returns
    -------
    (matplotlib.figure.Figure, matplotlib.axes.Axes)
        The created figure and axis for further customization or saving.
    """

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("The GPU metrics file is empty.")

    time_col = _pick_column(df, TIMESTAMP_COLUMNS, "timestamp")
    util_col = _pick_column(df, UTIL_COLUMNS, "GPU utilization percent")
    mem_col = _pick_column(df, MEM_COLUMNS, "GPU memory utilization percent")

    df[time_col] = pd.to_datetime(df[time_col])
    today = pd.Timestamp(datetime.now().date())
    tomorrow = today + pd.Timedelta(days=1)

    df = df[(df[time_col] >= today) & (df[time_col] < tomorrow)].copy()
    if df.empty:
        raise ValueError("No GPU metrics found for the current day.")

    df.sort_values(time_col, inplace=True)

    # Estimate a reasonable bar width from the median sampling interval.
    spacing = df[time_col].diff().median()
    if pd.isna(spacing) or spacing == pd.Timedelta(0):
        spacing = pd.Timedelta(minutes=5)
    bar_width = spacing / pd.Timedelta(days=1)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df[time_col], df[util_col], width=bar_width, alpha=0.6, label="GPU util %")
    ax.plot(df[time_col], df[mem_col], color="tab:orange", linewidth=2, label="GPU mem %")

    ax.set_title("GPU usage today")
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Percent")
    ax.set_ylim(0, max(100, df[[util_col, mem_col]].max().max()))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    ax.legend()
    fig.tight_layout()

    return fig, ax
