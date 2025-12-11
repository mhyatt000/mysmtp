"""Plot GPU metrics from a csv file.

This module focuses on plotting total GPU utilization and memory
utilization for the current day. It expects a timestamp column and
percentage columns for GPU utilization and GPU memory utilization.
"""

from __future__ import annotations
from mysmtp.subproc import do, parse, lines
import numpy as np

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
    print(df)
    if df.empty:
        raise ValueError("The GPU metrics file is empty.")

    time_col = _pick_column(df, TIMESTAMP_COLUMNS, "timestamp")
    util_col = _pick_column(df, UTIL_COLUMNS, "GPU utilization percent")
    # mem_col = _pick_column(df, MEM_COLUMNS, "GPU memory utilization percent")

    mem_used = "memory_used_MiB"
    mem_total = "memory_total_MiB"

    df[time_col] = pd.to_datetime(df[time_col])
    today = pd.Timestamp(datetime.now().date())
    tweek = today - pd.Timedelta(days=7)
    tomorrow = today + pd.Timedelta(days=1)

# Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp
    df[time_col] = df[time_col].dt.tz_localize(None)
    df = df[(df[time_col] >= tweek) & (df[time_col] < tomorrow)].copy()
    
    if df.empty:
        raise ValueError("No GPU metrics found for the current day.")

    # df = df.head(50) # select n rows for testing

    ids = set(df['index'].values)
    colors = plt.cm.get_cmap('tab10', len(ids)) # rgba
    colors = [np.array(colors(i)).round(2) for i in range(len(ids))]

    print(ids)
    print(colors)

    # group by index and plot each gpu separately
    fig, ax = plt.subplots(figsize=(12, 6))
    for k, gf in df.groupby('index'):

        gf.sort_values(time_col, inplace=True)

        # print(gf[util_col, mem_used, mem_total ])
        print(gf[[ util_col, mem_used, mem_total ]])

        # filter out values that did not change from previous row
        gf = gf.loc[(gf[util_col].shift() != gf[util_col]) | (gf[mem_used].shift() != gf[mem_used])]
        # print len
        print(f"GPU{k} rows after filtering: {len(gf)}")

        # Estimate a reasonable bar width from the median sampling interval.
        color = colors[k ]
        if k==0:
            spacing = gf[time_col].diff().median()

            if pd.isna(spacing) or spacing == pd.Timedelta(0):
                spacing = pd.Timedelta(minutes=5)
            bar_width = spacing / pd.Timedelta(days=1)

        ax.bar(gf[time_col], gf[util_col], width=bar_width, alpha=0.6, label=f"GPU{k} util %"
                , color=color   
               )

        mem_pct = (gf[mem_used] / gf[mem_total]) * 100
        ax.plot(gf[time_col],
                mem_pct,
                linestyle='--',
                color=color, linewidth=2, label=f"GPU{k} mem %")

    print('plotting')
    hostname = lines(do(parse("hostname"))[0])[0]
    ax.set_title(f"{hostname} GPU usage today")
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Percent")
    ax.set_ylim(0, 100)
                      

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    ax.legend()
    fig.tight_layout()

    return fig, ax
