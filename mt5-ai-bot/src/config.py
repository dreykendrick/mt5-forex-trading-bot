from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class StrategyConfig:
    breakout_N: int
    atr_period: int
    atr_min: float
    sl_atr_mult: float
    rr_ratio: float
    ema_period: int
    use_trend_filter: bool
    use_trailing_stop: bool
    trailing_atr_mult: float


@dataclass
class SessionConfig:
    timezone: str
    windows: List[Dict[str, str]]


@dataclass
class RiskConfig:
    risk_per_trade_pct: float
    daily_loss_limit_pct: float
    max_trades_per_day: int
    max_concurrent_positions_per_symbol: int


@dataclass
class ExecutionConfig:
    deviation: int
    max_spread_points: int
    slippage_points: int
    dry_run: bool
    retry_attempts: int
    retry_backoff_seconds: int
    kill_switch_file: str


@dataclass
class BacktestConfig:
    commission_per_lot: float
    spread_points: int
    slippage_points: int


@dataclass
class DataConfig:
    timezone: str
    output_dir: str


@dataclass
class AppConfig:
    symbols: List[str]
    timeframe: str
    strategy: StrategyConfig
    sessions: SessionConfig
    risk: RiskConfig
    execution: ExecutionConfig
    backtest: BacktestConfig
    data: DataConfig


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text())

    strategy = StrategyConfig(**raw["strategy"])
    sessions = SessionConfig(**raw["sessions"])
    risk = RiskConfig(**raw["risk"])
    execution = ExecutionConfig(**raw["execution"])
    backtest = BacktestConfig(**raw["backtest"])
    data = DataConfig(**raw["data"])

    return AppConfig(
        symbols=raw["symbols"],
        timeframe=raw["timeframe"],
        strategy=strategy,
        sessions=sessions,
        risk=risk,
        execution=execution,
        backtest=backtest,
        data=data,
    )


def load_yaml(path: str | Path) -> Dict[str, Any]:
    return yaml.safe_load(Path(path).read_text())
