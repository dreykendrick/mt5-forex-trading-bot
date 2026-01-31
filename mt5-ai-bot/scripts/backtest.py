from __future__ import annotations

import argparse

import MetaTrader5 as mt5

from src.backtest.costs import TradingCosts
from src.backtest.engine import run_backtest
from src.backtest.metrics import compute_metrics
from src.config import load_config
from src.data.loader import load_parquet
from src.execution.mt5_adapter import MT5Adapter
from src.utils.logging import configure_logging, get_logger


logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--initial-balance", type=float, default=10000)
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)

    data_path = f"{config.data.output_dir}/{args.symbol}_{config.timeframe}.parquet"
    df = load_parquet(data_path, tz=config.data.timezone)

    adapter = MT5Adapter(retry_attempts=1, retry_backoff_seconds=1)
    point = 0.0001
    tick_value = 10.0
    if adapter.initialize():
        info = mt5.symbol_info(args.symbol)
        if info is not None:
            point = info.point
            tick_value = info.trade_tick_value
        adapter.shutdown()

    result = run_backtest(
        df=df,
        initial_balance=args.initial_balance,
        breakout_N=config.strategy.breakout_N,
        atr_period=config.strategy.atr_period,
        atr_min=config.strategy.atr_min,
        sl_atr_mult=config.strategy.sl_atr_mult,
        rr_ratio=config.strategy.rr_ratio,
        ema_period=config.strategy.ema_period,
        use_trend_filter=config.strategy.use_trend_filter,
        risk_per_trade_pct=config.risk.risk_per_trade_pct,
        point=point,
        tick_value=tick_value,
        costs=TradingCosts(
            commission_per_lot=config.backtest.commission_per_lot,
            spread_points=config.backtest.spread_points,
            slippage_points=config.backtest.slippage_points,
        ),
    )

    metrics = compute_metrics(result.equity_curve, result.trades)
    logger.info("Backtest metrics", metrics.__dict__)


if __name__ == "__main__":
    main()
