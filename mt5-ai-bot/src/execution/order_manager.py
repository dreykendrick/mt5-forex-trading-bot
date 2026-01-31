from __future__ import annotations

from typing import Any, Dict, List, Optional

import MetaTrader5 as mt5

from src.execution.mt5_adapter import MT5Adapter
from src.execution.order_builder import OrderRequest, allowed_fillings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class OrderManager:
    def __init__(self, mt5_adapter: MT5Adapter):
        self.mt5_adapter = mt5_adapter

    def send_order_with_fillings(self, order_request: OrderRequest, symbol_info) -> Any:
        fillings = allowed_fillings(symbol_info)
        for filling in fillings:
            request = dict(order_request.request)
            request["type_filling"] = filling
            response = self.mt5_adapter.place_market_order(request)
            if response.result is None:
                return response
            if response.result.retcode == mt5.TRADE_RETCODE_DONE:
                return response
            if response.result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                logger.warning("Invalid filling mode, retrying", {"filling": filling})
                continue
            if response.result.retcode == mt5.TRADE_RETCODE_DONE:
                return response
            return response
        logger.error("All filling modes failed", {"symbol": symbol_info.name})
        return self.mt5_adapter.place_market_order(order_request.request)
