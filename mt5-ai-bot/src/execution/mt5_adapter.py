from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import MetaTrader5 as mt5

from src.utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class MT5Response:
    request: Dict[str, Any]
    result: Any


RET_CODES = {
    mt5.TRADE_RETCODE_REQUOTE: "Requote",
    mt5.TRADE_RETCODE_REJECT: "Rejected",
    mt5.TRADE_RETCODE_CANCEL: "Canceled",
    mt5.TRADE_RETCODE_PLACED: "Order placed",
    mt5.TRADE_RETCODE_DONE: "Order completed",
    mt5.TRADE_RETCODE_DONE_PARTIAL: "Order partial",
    mt5.TRADE_RETCODE_ERROR: "Common error",
    mt5.TRADE_RETCODE_TIMEOUT: "Timeout",
    mt5.TRADE_RETCODE_INVALID: "Invalid request",
    mt5.TRADE_RETCODE_INVALID_VOLUME: "Invalid volume",
    mt5.TRADE_RETCODE_INVALID_PRICE: "Invalid price",
    mt5.TRADE_RETCODE_INVALID_STOPS: "Invalid stops",
    mt5.TRADE_RETCODE_TRADE_DISABLED: "Trade disabled",
    mt5.TRADE_RETCODE_MARKET_CLOSED: "Market closed",
    mt5.TRADE_RETCODE_NO_MONEY: "Not enough money",
    mt5.TRADE_RETCODE_PRICE_CHANGED: "Price changed",
    mt5.TRADE_RETCODE_PRICE_OFF: "Off quotes",
    mt5.TRADE_RETCODE_INVALID_EXPIRATION: "Invalid expiration",
    mt5.TRADE_RETCODE_ORDER_CHANGED: "Order changed",
    mt5.TRADE_RETCODE_TOO_MANY_REQUESTS: "Too many requests",
    mt5.TRADE_RETCODE_NO_CHANGES: "No changes",
    mt5.TRADE_RETCODE_SERVER_DISABLES_AT: "Server disables",
    mt5.TRADE_RETCODE_CLIENT_DISABLES_AT: "Client disables",
    mt5.TRADE_RETCODE_LOCKED: "Locked",
    mt5.TRADE_RETCODE_FROZEN: "Frozen",
}


class MT5Adapter:
    def __init__(self, retry_attempts: int, retry_backoff_seconds: int):
        self.retry_attempts = retry_attempts
        self.retry_backoff_seconds = retry_backoff_seconds

    def initialize(self) -> bool:
        if not mt5.initialize():
            logger.error("MT5 initialize failed", {"error": mt5.last_error()})
            return False
        logger.info("MT5 initialized")
        return True

    def shutdown(self) -> None:
        mt5.shutdown()
        logger.info("MT5 shutdown")

    def get_symbol_info(self, symbol: str):
        info = mt5.symbol_info(symbol)
        if info is None:
            logger.error("Symbol info not found", {"symbol": symbol})
        return info

    def get_tick(self, symbol: str):
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error("Tick not available", {"symbol": symbol})
        return tick

    def order_check(self, request: Dict[str, Any]):
        return mt5.order_check(request)

    def order_send(self, request: Dict[str, Any]):
        return mt5.order_send(request)

    def place_market_order(self, request: Dict[str, Any]) -> MT5Response:
        for attempt in range(1, self.retry_attempts + 1):
            check = self.order_check(request)
            if check is None or check.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error("Order check failed", {"retcode": getattr(check, "retcode", None), "comment": getattr(check, "comment", None)})
                return MT5Response(request=request, result=check)

            result = self.order_send(request)
            if result is None:
                logger.error("Order send failed", {"error": mt5.last_error()})
                return MT5Response(request=request, result=result)

            if result.retcode in {mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_PLACED}:
                logger.info("Order executed", {"retcode": result.retcode})
                return MT5Response(request=request, result=result)

            if result.retcode in {mt5.TRADE_RETCODE_REQUOTE, mt5.TRADE_RETCODE_PRICE_CHANGED, mt5.TRADE_RETCODE_PRICE_OFF, mt5.TRADE_RETCODE_TRADE_CONTEXT_BUSY}:
                logger.warning("Transient error, retrying", {"retcode": result.retcode, "attempt": attempt})
                time.sleep(self.retry_backoff_seconds)
                continue

            logger.error("Order send error", {"retcode": result.retcode, "comment": result.comment})
            return MT5Response(request=request, result=result)

        logger.error("Order send exceeded retries", {"request": request})
        return MT5Response(request=request, result=None)

    def modify_position_sl_tp(self, request: Dict[str, Any]) -> MT5Response:
        result = self.order_send(request)
        if result is None:
            logger.error("Modify order failed", {"error": mt5.last_error()})
        else:
            logger.info("Modify order result", {"retcode": result.retcode, "comment": result.comment})
        return MT5Response(request=request, result=result)

    @staticmethod
    def retcode_message(retcode: int) -> str:
        return RET_CODES.get(retcode, "Unknown retcode")
