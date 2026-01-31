from __future__ import annotations


import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR))


import argparse
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd

from src.config import load_config
from src.data.storage import save_parquet
from src.execution.mt5_adapter import MT5Adapter
from src.utils.logging import configure_logging, get_logger


logger = get_logger(__name__)


TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)

    adapter = MT5Adapter(retry_attempts=1, retry_backoff_seconds=1)
    if not adapter.initialize():
        return

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)

    for symbol in config.symbols:
        timeframe = TIMEFRAME_MAP[config.timeframe]
        rates = mt5.copy_rates_range(symbol, timeframe, start, end)
        if rates is None:
            logger.error("Failed to download rates", {"symbol": symbol})
            continue
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        out_path = f"{config.data.output_dir}/{symbol}_{config.timeframe}.parquet"
        save_parquet(df, out_path)
        logger.info("Saved data", {"symbol": symbol, "path": out_path})

    adapter.shutdown()


if __name__ == "__main__":
    main()
