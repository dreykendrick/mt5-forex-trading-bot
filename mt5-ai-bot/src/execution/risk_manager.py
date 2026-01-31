from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RiskLimits:
    risk_per_trade_pct: float
    daily_loss_limit_pct: float
    max_trades_per_day: int
    max_concurrent_positions_per_symbol: int


@dataclass
class RiskState:
    day: str = ""
    trades_today: int = 0
    realized_pnl_today: float = 0.0


@dataclass
class RiskManager:
    limits: RiskLimits
    state: RiskState = field(default_factory=RiskState)

    def reset_if_new_day(self, now: datetime) -> None:
        day = now.strftime("%Y-%m-%d")
        if day != self.state.day:
            self.state.day = day
            self.state.trades_today = 0
            self.state.realized_pnl_today = 0.0

    def record_trade(self, pnl: float) -> None:
        self.state.trades_today += 1
        self.state.realized_pnl_today += pnl

    def can_trade(self, balance: float) -> tuple[bool, str]:
        if self.state.trades_today >= self.limits.max_trades_per_day:
            return False, "max_trades_per_day"
        daily_loss_limit = -balance * (self.limits.daily_loss_limit_pct / 100)
        if self.state.realized_pnl_today <= daily_loss_limit:
            return False, "daily_loss_limit"
        return True, "ok"

    def position_size_lots(
        self,
        balance: float,
        sl_distance: float,
        point: float,
        tick_value: float,
        volume_step: float,
        volume_min: float,
        volume_max: float,
    ) -> float:
        risk_amount = balance * (self.limits.risk_per_trade_pct / 100)
        if sl_distance <= 0 or point <= 0 or tick_value <= 0:
            return 0.0
        raw_lots = risk_amount / (sl_distance / point * tick_value)
        rounded = round(raw_lots / volume_step) * volume_step
        return min(max(rounded, volume_min), volume_max)
