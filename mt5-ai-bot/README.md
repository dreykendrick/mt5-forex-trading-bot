# MT5 AI Bot (ATR-Filtered Breakout)

Production-ready, MT5-compatible forex trading bot in Python. Includes a configurable ATR-filtered breakout strategy, backtesting engine, live trading execution, risk management, and monitoring.

## ⚠️ Risk Warning
Trading leveraged FX is **high risk**. This project is for educational and professional use only. You are responsible for ensuring compliance with broker rules and local regulations. Use on demo accounts first.

## Features
- MT5 live trading via `MetaTrader5` package
- ATR-filtered breakout strategy (H1 default)
- Risk management: fixed fractional risk, daily loss limit, max trades per day, max concurrent positions
- Safeguards: symbol tradability checks, session filters, kill switch, spread limits
- Backtesting engine with spread, commission, slippage
- Structured logs + trade journal CSV + optional Telegram alerts
- Config-driven design (YAML)
- DRY_RUN (paper trading) mode

## Project Structure
```
mt5-ai-bot/
  README.md
  requirements.txt
  config.yaml
  .env.example
  .gitignore
  scripts/
    backtest.py
    run_live.py
    download_data.py
    sanity_check_mt5.py
  src/
    __init__.py
    config.py
    utils/
      __init__.py
      logging.py
      timeutils.py
      mathutils.py
    data/
      __init__.py
      loader.py
      storage.py
    strategy/
      __init__.py
      atr_breakout.py
    backtest/
      __init__.py
      engine.py
      metrics.py
      costs.py
    execution/
      __init__.py
      mt5_adapter.py
      order_builder.py
      order_manager.py
      risk_manager.py
      safeguards.py
    monitoring/
      __init__.py
      journal.py
      alerts.py
  tests/
    test_risk_manager.py
    test_strategy_atr_breakout.py
    test_order_builder.py
```

## Setup
### 1) Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2) Configure MT5 Terminal
- Install MetaTrader 5 on a Windows VPS.
- Login to your broker account.
- Keep MT5 running and logged in.

### 3) Configure the Bot
Edit `config.yaml` for symbols, session hours, risk limits, and strategy parameters.

Optional Telegram alerts:
```bash
cp .env.example .env
# Fill TELEGRAM_TOKEN and TELEGRAM_CHAT_ID
```

## Sanity Check MT5
```bash
python scripts/sanity_check_mt5.py
```
This prints account info, symbol properties, and tick data availability.

## Download Data (for Backtest)
```bash
python scripts/download_data.py --start 2020-01-01 --end 2024-01-01
```
Outputs Parquet files to `data/processed/`.

## Run Backtest
```bash
python scripts/backtest.py --symbol EURUSD
```

## Paper Trading (DRY_RUN)
```bash
python scripts/run_live.py --dry-run
```

## Go Live (VPS)
```bash
python scripts/run_live.py
```

## Troubleshooting
- **Retcode 10030 (invalid filling):** Ensure `type_filling` matches `symbol_info.filling_mode` and broker supports it.
- **Retcode 10027 (invalid stops):** Ensure SL/TP respects `stops_level` + safety buffer.
- **No ticks / market closed:** Confirm symbol is available and market open.
- **Trade context busy / requotes:** Built-in retries handle transient issues; check logs if repeated.


## Safety Notes
- Use demo account for initial testing.
- Set conservative risk (default 0.5% per trade).
- Always monitor logs and journal.
- Use kill switch file `./KILL_SWITCH` to stop new trades immediately.
