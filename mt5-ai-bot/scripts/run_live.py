from __future__ import annotations


import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR))


import argparse
import time
from datetime import datetime, timezone

import MetaTrader5 as mt5
import pandas as pd
from dotenv import load_dotenv

from src.config import load_config
from src.execution.mt5_adapter import MT5Adapter
from src.execution.order_builder import build_market_order_request, build_sl_tp_request
from src.execution.order_manager import OrderManager
from src.execution.risk_manager import RiskLimits, RiskManager
from src.execution.safeguards import kill_switch_active, is_symbol_tradable, spread_too_high, stops_level_ok
from src.monitoring.alerts import load_telegram_alert
from src.monitoring.journal import TradeJournal
from src.strategy.atr_breakout import compute_signal
from src.utils.logging import configure_logging, get_logger
from src.utils.timeutils import is_in_session, parse_sessions


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


def fetch_rates(symbol: str, timeframe: int, bars: int) -> pd.DataFrame:
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time")
    df = df.rename(columns={"open": "open", "high": "high", "low": "low", "close": "close", "tick_volume": "volume"})
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    configure_logging()
    load_dotenv()
    config = load_config(args.config)

    adapter = MT5Adapter(
        retry_attempts=config.execution.retry_attempts,
        retry_backoff_seconds=config.execution.retry_backoff_seconds,
    )
    if not adapter.initialize():
        return

    alert = load_telegram_alert()
    journal = TradeJournal(path="trades/trade_journal.csv")
    risk_manager = RiskManager(
        limits=RiskLimits(
            risk_per_trade_pct=config.risk.risk_per_trade_pct,
            daily_loss_limit_pct=config.risk.daily_loss_limit_pct,
            max_trades_per_day=config.risk.max_trades_per_day,
            max_concurrent_positions_per_symbol=config.risk.max_concurrent_positions_per_symbol,
        )
    )

    tz, windows = parse_sessions(config.sessions.timezone, config.sessions.windows)
    timeframe = TIMEFRAME_MAP[config.timeframe]

    last_bar_time = {}

    try:
        while True:
            now = datetime.now(timezone.utc)
            risk_manager.reset_if_new_day(now)

            if kill_switch_active(config.execution.kill_switch_file):
                logger.warning("Kill switch active. No new trades.")
                time.sleep(5)
                continue

            for symbol in config.symbols:
                info = adapter.get_symbol_info(symbol)
                if not is_symbol_tradable(info):
                    logger.warning("Symbol not tradable", {"symbol": symbol})
                    continue

                tick = adapter.get_tick(symbol)
                if tick is None:
                    continue

                if spread_too_high(tick, config.execution.max_spread_points, info.point):
                    logger.warning("Spread too high", {"symbol": symbol})
                    continue

                if not is_in_session(now, tz, windows):
                    continue

                rates = fetch_rates(symbol, timeframe, max(config.strategy.breakout_N, config.strategy.atr_period, config.strategy.ema_period) + 5)
                if rates.empty:
                    continue

                bar_time = rates.index[-1]
                if last_bar_time.get(symbol) == bar_time:
                    continue
                last_bar_time[symbol] = bar_time

                signal = compute_signal(
                    rates,
                    breakout_N=config.strategy.breakout_N,
                    atr_period=config.strategy.atr_period,
                    atr_min=config.strategy.atr_min,
                    ema_period=config.strategy.ema_period,
                    use_trend_filter=config.strategy.use_trend_filter,
                )

                if signal.direction == 0:
                    continue

                can_trade, reason = risk_manager.can_trade(balance=mt5.account_info().balance)
                if not can_trade:
                    logger.warning("Risk limits block trade", {"reason": reason})
                    continue

                sl_distance = config.strategy.sl_atr_mult * signal.atr_value
                if sl_distance <= 0:
                    continue

                entry = tick.ask if signal.direction == 1 else tick.bid
                sl = entry - sl_distance if signal.direction == 1 else entry + sl_distance
                tp = entry + config.strategy.rr_ratio * sl_distance if signal.direction == 1 else entry - config.strategy.rr_ratio * sl_distance

                ok, min_dist = stops_level_ok(info, sl, tp, entry)
                if not ok:
                    logger.warning("Stops too close", {"symbol": symbol, "min_distance": min_dist})
                    continue

                volume = risk_manager.position_size_lots(
                    balance=mt5.account_info().balance,
                    sl_distance=sl_distance,
                    point=info.point,
                    tick_value=info.trade_tick_value,
                    volume_step=info.volume_step,
                    volume_min=info.volume_min,
                    volume_max=info.volume_max,
                )
                if volume <= 0:
                    continue

                action = mt5.ORDER_TYPE_BUY if signal.direction == 1 else mt5.ORDER_TYPE_SELL
                order_req = build_market_order_request(
                    symbol=symbol,
                    action=action,
                    volume=volume,
                    price=entry,
                    deviation=config.execution.deviation,
                    sl=sl,
                    tp=tp,
                    symbol_info=info,
                )

                if args.dry_run or config.execution.dry_run:
                    logger.info("DRY_RUN order", {"symbol": symbol, "direction": signal.direction, "volume": volume, "entry": entry, "sl": sl, "tp": tp})
                    continue

                manager = OrderManager(adapter)
                response = manager.send_order_with_fillings(order_req, info)
                result = response.result

                if result is None:
                    continue

                if result.retcode == mt5.TRADE_RETCODE_INVALID_STOPS:
                    logger.warning("Invalid stops, retry without SL/TP", {"symbol": symbol})
                    order_req = build_market_order_request(
                        symbol=symbol,
                        action=action,
                        volume=volume,
                        price=entry,
                        deviation=config.execution.deviation,
                        sl=None,
                        tp=None,
                        symbol_info=info,
                    )
                    response = manager.send_order_with_fillings(order_req, info)
                    result = response.result
                    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                        continue
                    modify_req = build_sl_tp_request(result.order, symbol, sl, tp)
                    adapter.modify_position_sl_tp(modify_req)

                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    journal.append(
                        {
                            "time": datetime.now(timezone.utc).isoformat(),
                            "symbol": symbol,
                            "direction": "BUY" if signal.direction == 1 else "SELL",
                            "volume": volume,
                            "price": entry,
                            "sl": sl,
                            "tp": tp,
                            "ticket": result.order,
                            "comment": result.comment,
                        }
                    )
                    alert.send(f"Trade executed {symbol} {signal.direction} @ {entry}")

            time.sleep(10)
    finally:
        adapter.shutdown()


if __name__ == "__main__":
    main()
