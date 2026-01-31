from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

import MetaTrader5 as mt5

from src.config import load_config
from src.execution.mt5_adapter import MT5Adapter
from src.utils.logging import configure_logging, get_logger


logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    config = load_config("config.yaml")

    adapter = MT5Adapter(retry_attempts=1, retry_backoff_seconds=1)
    if not adapter.initialize():
        return

    account = mt5.account_info()
    logger.info("Account info", {"account": account._asdict() if account else None})

    for symbol in config.symbols:
        selected = mt5.symbol_select(symbol, True)
        info = mt5.symbol_info(symbol)
        tick = mt5.symbol_info_tick(symbol)
        logger.info(
            "Symbol info",
            {
                "symbol": symbol,
                "selected": selected,
                "filling_mode": getattr(info, "filling_mode", None),
                "stops_level": getattr(info, "stops_level", None),
                "volume_min": getattr(info, "volume_min", None),
                "volume_step": getattr(info, "volume_step", None),
                "volume_max": getattr(info, "volume_max", None),
            },
        )
        logger.info("Tick", {"symbol": symbol, "tick": tick._asdict() if tick else None})

    adapter.shutdown()


if __name__ == "__main__":
    main()
