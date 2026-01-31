from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_parquet(path: str | Path, tz: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert(tz)
        df = df.set_index("time")
    return df
