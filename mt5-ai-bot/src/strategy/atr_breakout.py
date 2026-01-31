from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.utils.mathutils import atr, ema


@dataclass
class Signal:
    direction: int  # 1 buy, -1 sell, 0 none
    atr_value: float
    breakout_high: float
    breakout_low: float
    ema_slope: float


def compute_signal(df: pd.DataFrame, breakout_N: int, atr_period: int, atr_min: float, ema_period: int,
                   use_trend_filter: bool) -> Signal:
    if len(df) < max(breakout_N, atr_period, ema_period) + 1:
        return Signal(0, 0.0, 0.0, 0.0, 0.0)

    df = df.copy()
    df["atr"] = atr(df, atr_period)
    df["ema"] = ema(df["close"], ema_period)

    recent = df.iloc[-1]
    prior = df.iloc[-(breakout_N + 1):-1]
    breakout_high = prior["high"].max()
    breakout_low = prior["low"].min()
    atr_value = float(recent["atr"])
    ema_slope = float(df["ema"].iloc[-1] - df["ema"].iloc[-2])

    if pd.isna(atr_value) or atr_value < atr_min:
        return Signal(0, atr_value, breakout_high, breakout_low, ema_slope)

    close = float(recent["close"])
    direction = 0
    if close > breakout_high:
        direction = 1
    elif close < breakout_low:
        direction = -1

    if use_trend_filter and direction != 0:
        if direction == 1 and ema_slope <= 0:
            direction = 0
        if direction == -1 and ema_slope >= 0:
            direction = 0

    return Signal(direction, atr_value, breakout_high, breakout_low, ema_slope)
