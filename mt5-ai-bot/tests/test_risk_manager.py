from src.execution.risk_manager import RiskLimits, RiskManager


def test_position_size_lots():
    limits = RiskLimits(
        risk_per_trade_pct=1.0,
        daily_loss_limit_pct=2.0,
        max_trades_per_day=3,
        max_concurrent_positions_per_symbol=1,
    )
    rm = RiskManager(limits=limits)
    lots = rm.position_size_lots(
        balance=10000,
        sl_distance=0.0010,
        point=0.0001,
        tick_value=10,
        volume_step=0.01,
        volume_min=0.01,
        volume_max=1.0,
    )
    assert lots > 0
    assert lots <= 1.0
