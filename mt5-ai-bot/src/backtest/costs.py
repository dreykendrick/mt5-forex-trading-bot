from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradingCosts:
    commission_per_lot: float
    spread_points: int
    slippage_points: int

    def spread_cost(self, point_value: float) -> float:
        return self.spread_points * point_value

    def slippage_cost(self, point_value: float) -> float:
        return self.slippage_points * point_value
