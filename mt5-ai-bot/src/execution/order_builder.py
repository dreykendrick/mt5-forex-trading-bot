from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import MetaTrader5 as mt5

from src.utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class OrderRequest:
    request: Dict[str, Any]
    filling_mode: int


def allowed_fillings(symbol_info) -> List[int]:
    modes = []
    bitmask = getattr(symbol_info, "filling_modes", 0)
    for mode in [mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_RETURN]:
        if bitmask == 0:
            modes.append(symbol_info.filling_mode)
            break
        if bitmask & mode:
            modes.append(mode)
    if not modes:
        modes.append(symbol_info.filling_mode)
    return list(dict.fromkeys(modes))


def build_market_order_request(
    symbol: str,
    action: int,
    volume: float,
    price: float,
    deviation: int,
    sl: float | None,
    tp: float | None,
    symbol_info,
    magic: int = 123456,
    comment: str = "ATRBreakout",
) -> OrderRequest:
    fillings = allowed_fillings(symbol_info)
    filling_mode = fillings[0]

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": action,
        "price": price,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    if sl is not None:
        request["sl"] = sl
    if tp is not None:
        request["tp"] = tp

    logger.info("Built order request", {"request": request})
    return OrderRequest(request=request, filling_mode=filling_mode)


def build_sl_tp_request(position_ticket: int, symbol: str, sl: float, tp: float) -> Dict[str, Any]:
    return {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": position_ticket,
        "symbol": symbol,
        "sl": sl,
        "tp": tp,
    }
