from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.backtest.costs import TradingCosts
from src.strategy.atr_breakout import compute_signal
from src.utils.mathutils import atr


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame


def run_backtest(
    df: pd.DataFrame,
    initial_balance: float,
    breakout_N: int,
    atr_period: int,
    atr_min: float,
    sl_atr_mult: float,
    rr_ratio: float,
    ema_period: int,
    use_trend_filter: bool,
    risk_per_trade_pct: float,
    point: float,
    tick_value: float,
    costs: TradingCosts,
) -> BacktestResult:
    df = df.copy()
    df["atr"] = atr(df, atr_period)

    balance = initial_balance
    equity_curve = []
    trades = []
    position = None

    for idx in range(max(breakout_N, atr_period, ema_period) + 1, len(df)):
        row = df.iloc[idx]
        timestamp = df.index[idx]

        if position:
            high = row["high"]
            low = row["low"]
            exit_price = None
            if position["direction"] == 1:
                if low <= position["sl"]:
                    exit_price = position["sl"]
                elif high >= position["tp"]:
                    exit_price = position["tp"]
            else:
                if high >= position["sl"]:
                    exit_price = position["sl"]
                elif low <= position["tp"]:
                    exit_price = position["tp"]

            if exit_price is not None:
                pnl = (exit_price - position["entry"]) * position["direction"]
                pnl_value = pnl / point * tick_value * position["lots"]
                pnl_value -= costs.commission_per_lot * position["lots"]
                pnl_value -= costs.spread_cost(tick_value) + costs.slippage_cost(tick_value)
                balance += pnl_value
                trades.append(
                    {
                        "entry_time": position["time"],
                        "exit_time": timestamp,
                        "direction": position["direction"],
                        "entry": position["entry"],
                        "exit": exit_price,
                        "lots": position["lots"],
                        "pnl": pnl_value,
                        "r_multiple": pnl_value / position["risk_amount"],
                    }
                )
                position = None

        if position is None:
            subset = df.iloc[: idx + 1]
            signal = compute_signal(
                subset,
                breakout_N=breakout_N,
                atr_period=atr_period,
                atr_min=atr_min,
                ema_period=ema_period,
                use_trend_filter=use_trend_filter,
            )
            if signal.direction != 0:
                entry = row["close"]
                atr_value = signal.atr_value
                sl_distance = sl_atr_mult * atr_value
                if sl_distance <= 0:
                    equity_curve.append(balance)
                    continue
                sl = entry - sl_distance if signal.direction == 1 else entry + sl_distance
                tp = entry + rr_ratio * sl_distance if signal.direction == 1 else entry - rr_ratio * sl_distance
                risk_amount = balance * (risk_per_trade_pct / 100)
                lots = risk_amount / (sl_distance / point * tick_value)
                position = {
                    "time": timestamp,
                    "direction": signal.direction,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "lots": max(lots, 0),
                    "risk_amount": risk_amount,
                }

        equity_curve.append(balance)

    equity_series = pd.Series(equity_curve, index=df.index[max(breakout_N, atr_period, ema_period) + 1 :])
    trades_df = pd.DataFrame(trades)
    return BacktestResult(equity_curve=equity_series, trades=trades_df)
