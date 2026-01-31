from __future__ import annotations

from pathlib import Path

import pandas as pd


def save_parquet(df: pd.DataFrame, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(out, index=False)
    except ImportError as exc:
        raise ImportError(
            "Parquet support requires 'pyarrow'. Install with 'pip install pyarrow' "
            "or use Python 3.10–3.12 on Windows for prebuilt wheels."
        ) from exc
