from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestMetrics:
    cagr: float
    max_drawdown: float
    profit_factor: float
    sharpe: float
    win_rate: float
    avg_r_multiple: float


def compute_metrics(equity_curve: pd.Series, trades: pd.DataFrame) -> BacktestMetrics:
    returns = equity_curve.pct_change().dropna()
    if returns.empty:
        return BacktestMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    cagr = (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (252 / len(returns)) - 1
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min()

    profits = trades["pnl"].clip(lower=0).sum()
    losses = trades["pnl"].clip(upper=0).abs().sum()
    profit_factor = profits / losses if losses > 0 else float("inf")

    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
    win_rate = (trades["pnl"] > 0).mean() if not trades.empty else 0.0
    avg_r_multiple = trades["r_multiple"].mean() if not trades.empty else 0.0

    return BacktestMetrics(
        cagr=cagr,
        max_drawdown=max_drawdown,
        profit_factor=profit_factor,
        sharpe=sharpe,
        win_rate=win_rate,
        avg_r_multiple=avg_r_multiple,
    )
