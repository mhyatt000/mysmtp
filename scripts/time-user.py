#!/usr/bin/env python3
from tqdm import tqdm
import subprocess
import re

from dataclasses import dataclass
import tyro


import subprocess
import pandas as pd
from datetime import datetime
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich import print

from mysmtp.subproc import do, parse, lines

console = Console()

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

def parse_datetime(parts):
    # Example: ['Wed','Dec','10','14:51:16','2025']
    if len(parts) != 5:
        return None
    _, mon, day, t, year = parts
    hour, minute, sec = map(int, t.split(":"))
    return datetime(
        int(year),
        MONTH_MAP[mon],
        int(day),
        hour,
        minute,
        sec
    )

def duration_str(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    hours = hours % 24
    minutes = minutes % 60
    return f"{int(days)}d {int(hours):02d}:{int(minutes):02d}"
    return f"{int(hours):02d}:{int(minutes):02d}"

# -------------------------------------------------------------------------
# PARSER for `last -aF` lines
# -------------------------------------------------------------------------

def parse_last_line(line):
    """
    Produces:
    {
        'user': ...,
        'tty': ...,
        'start': datetime,
        'end': datetime or None,
        'remote': ...,
    }
    or None if reboot / invalid
    """

    if line.startswith("reboot"):
        return None  # ignore reboot lines for usage stats

    # Basic tokenization
    tokens = line.split()

    # Must have at least: user tty Day Mon DD HH:MM:SS YYYY ...
    if len(tokens) < 10:
        return None

    user = tokens[0]
    tty = tokens[1]

    # Case 1: still logged in -----------------------------------------
    if "still" in tokens:
        # Example:
        # mhyatt pts/5 Wed Dec 10 14:51:16 2025 still logged in  IP
        i = tokens.index("still")
        start = parse_datetime(tokens[2:7])
        end = None
        remote = tokens[-1]
        return dict(user=user, tty=tty, start=start, end=end, remote=remote)

    # Case 2: has logout timestamp ------------------------------------
    # Format:
    # user tty  DOW Mon DD HH:MM:SS YYYY - DOW Mon DD HH:MM:SS YYYY (duration) remote

    # Find " - "
    if "-" not in tokens:
        return None

    i = tokens.index("-")

    start = parse_datetime(tokens[2:i])  # [DOW Mon DD HH:MM:SS YYYY]

    # logout tokens start after "-"
    # find where the duration "(hh:mm)" starts
    # duration begins with '('
    j = None
    for k in range(i+1, len(tokens)):
        if tokens[k].startswith("("):
            j = k
            break
    if j is None:
        return None

    end_tokens = tokens[i+1:j]  # ["DOW","Mon","DD","HH:MM:SS","YYYY"]
    end = parse_datetime(end_tokens)

    # last token is remote host
    remote = tokens[-1]

    return dict(user=user, tty=tty, start=start, end=end, remote=remote)

# -------------------------------------------------------------------------
# MAIN: run last, parse, compute durations
# -------------------------------------------------------------------------

def collect_usage_df():
    """
    Returns a pandas DataFrame with columns:
    user, tty, remote, start, end, duration_seconds
    """
    # Run last -aF
    p = subprocess.run(["last", "-aF"], capture_output=True, text=True)
    lines = p.stdout.splitlines()

    rows = []
    now = datetime.now()

    for line in lines:
        entry = parse_last_line(line)   # your existing parser
        if not entry:
            continue

        start = entry["start"]
        end   = entry["end"] or now

        duration = (end - start).total_seconds()

        rows.append({
            "user": entry["user"],
            "tty": entry["tty"],
            "remote": entry["remote"],
            "start": start,
            "end": end,
            "duration_seconds": duration,
        })

    # Build DataFrame
    df = pd.DataFrame(rows)

    # Sort by user then start time for convenience
    if not df.empty:
        df = df.sort_values(["user", "start"]).reset_index(drop=True)

    return df

# -------------------------------------------------------------------------
# Pretty output
# -------------------------------------------------------------------------

def print_summary(totals):
    table = Table(title="User Login Time Summary")

    table.add_column("User", justify="left", style="cyan")
    table.add_column("Total Time (HH:MM)", justify="right", style="green")

    for user, sec in totals.items():
        table.add_row(user, duration_str(sec))

    console.print(table)


def print_items_table(items):
    # --- Normalize input ---
    if hasattr(items, "to_dict"):          # it's a DataFrame
        items = items.to_dict(orient="records")
    elif not isinstance(items, list):      # safety
        raise TypeError("items must be a list[dict] or a pandas DataFrame")

    if not items:
        console.print("[yellow]No data.[/yellow]")
        return

    columns = list(items[0].keys())

    table = Table(title="Results")
    for col in columns:
        table.add_column(col, style="cyan")

    for item in items:
        table.add_row(*[str(item[col]) for col in columns])

    console.print(table)


import pandas as pd
import numpy as np

def make_15min_blocks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input columns:
        user, start (datetime), end (datetime)
    Output:
        user, block_start (datetime)  -- one row per 15-min block of activity
    """

    # Ensure datetime
    df = df.copy()
    df["start"] = pd.to_datetime(df["start"])
    df["end"]   = pd.to_datetime(df["end"])

    blocks = []

    for user, g in tqdm(df.groupby("user")):
        # Collect all 15-min bins from all sessions
        bins = set()

        nrows = len(g)
        for _, row in tqdm(g.iterrows(), total=nrows, desc=f"User {user}"):
            s, e = row["start"], row["end"]

            # Snap start downward to nearest 15-min mark
            start_block = s.floor("15min")

            # Generate 15-min ticks until end
            t = start_block
            while t <= e:
                bins.add(t)
                t += pd.Timedelta(minutes=15)

        # Store
        for b in bins:
            blocks.append({"user": user, "start": b
                           })

    blocks_df = pd.DataFrame(blocks)
    return blocks_df.sort_values(["user", "start"]).reset_index(drop=True)


@dataclass 
class Config:
    pass

def main(cfg: Config) -> None:

    df = collect_usage_df()

    # filter by start in the last 7 days
    now = datetime.now()
    week_ago = now - pd.Timedelta(days=3)
    df = df[df["start"] >= week_ago]

    print(df.columns)
    blocks = make_15min_blocks(df)
    # blocks = blocks.drop(columns=["tty", "remote"])
    blocks["duration_seconds"] = 15 * 60  # each block is 15 minutes
    print(blocks.columns)

    # group by user and sum durations
    totals = blocks.groupby("user")["duration_seconds"].sum().reset_index()
    # convert duration_seconds to DD:HH:MM format
    totals["duration"] = totals["duration_seconds"].apply(duration_str)
    totals = totals.drop(columns=["duration_seconds"])
    print_items_table(totals)

    quit()
    # .groupby("user")["duration_seconds"].agg(['sum', 'count']).reset_index()
    # .to_dict(orient='records'), collect_usage_df().to_dict(orient='records')

if __name__ == "__main__":
    main(tyro.cli(Config))
