import MetaTrader5 as mt5

from src.execution.order_builder import allowed_fillings, build_market_order_request


class MockSymbol:
    def __init__(self, filling_mode, filling_modes):
        self.filling_mode = filling_mode
        self.filling_modes = filling_modes


def test_allowed_fillings_from_bitmask():
    symbol = MockSymbol(mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_FOK | mt5.ORDER_FILLING_IOC)
    modes = allowed_fillings(symbol)
    assert mt5.ORDER_FILLING_FOK in modes
    assert mt5.ORDER_FILLING_IOC in modes


def test_build_order_request():
    symbol = MockSymbol(mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_FOK)
    req = build_market_order_request(
        symbol="EURUSD",
        action=mt5.ORDER_TYPE_BUY,
        volume=0.1,
        price=1.2345,
        deviation=10,
        sl=1.2300,
        tp=1.2400,
        symbol_info=symbol,
    )
    assert req.request["symbol"] == "EURUSD"
    assert req.request["type_filling"] == mt5.ORDER_FILLING_FOK
