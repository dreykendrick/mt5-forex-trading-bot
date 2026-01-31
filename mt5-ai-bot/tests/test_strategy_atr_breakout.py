import pandas as pd

from src.strategy.atr_breakout import compute_signal


def test_breakout_signal_buy():
    data = {
        "open": [1, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.25],
        "high": [1.01] * 20 + [1.30],
        "low": [0.99] * 20 + [1.20],
        "close": [1.00] * 20 + [1.28],
    }
    df = pd.DataFrame(data)
    signal = compute_signal(df, breakout_N=20, atr_period=14, atr_min=0.0001, ema_period=5, use_trend_filter=False)
    assert signal.direction == 1
