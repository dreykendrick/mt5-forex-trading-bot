# MT5 Forex Trading Bot

A sophisticated automated trading bot for MetaTrader 5 (MT5) that executes forex trading strategies using technical analysis and risk management principles.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Workflow](#project-workflow)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Folder Structure](#folder-structure)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Risk Management](#risk-management)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

The MT5 Forex Trading Bot is an automated trading solution designed to execute forex trading strategies on MetaTrader 5 platforms. The bot leverages technical analysis indicators, algorithmic decision-making, and strict risk management protocols to identify and execute trading opportunities in the forex market.

### Key Objectives:
- Automate forex trading strategies with minimal human intervention
- Implement consistent risk management across all trades
- Provide real-time market analysis and trading signals
- Maintain detailed trade logs and performance metrics
- Enable easy strategy customization and backtesting

## ✨ Features

- **Automated Trading**: Executes trades based on predefined technical indicators and strategy rules
- **Multiple Currency Pairs**: Support for major forex pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- **Technical Indicators**: Integration of moving averages, RSI, MACD, Bollinger Bands, and more
- **Risk Management**: Position sizing, stop-loss, take-profit, and daily loss limits
- **Trade Logging**: Comprehensive logging of all trades, signals, and performance metrics
- **Real-time Monitoring**: Live market price monitoring and trade execution
- **Backtesting Support**: Historical data analysis for strategy validation
- **Configurable Parameters**: Easy customization of strategy parameters
- **Error Handling**: Robust error handling and logging mechanisms
- **MT5 Integration**: Direct connection to MetaTrader 5 platform via Python

## 🔄 Project Workflow

### Trading Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. Market Data Collection                     │
│         Fetch real-time OHLC data for selected pairs             │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               2. Technical Analysis & Indicators                 │
│    Calculate MA, RSI, MACD, Bollinger Bands, and other signals   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              3. Strategy Evaluation & Signal Generation          │
│   Evaluate conditions and generate BUY/SELL/HOLD signals         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│            4. Risk Management & Position Sizing                  │
│    Calculate position size based on account equity and risk      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│            5. Trade Execution (Place Order)                      │
│    Send BUY/SELL orders with SL and TP to MT5 platform          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│            6. Trade Monitoring & Management                      │
│    Monitor open trades, manage position, handle closures         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│         7. Logging & Performance Tracking                        │
│    Record trade data, calculate metrics, update statistics       │
└─────────────────────────────────────────────────────────────────┘
```

### Decision Logic Flow

```
Are conditions met for:
├── BUY Signal?
│   ├── Yes → Execute BUY order
│   └── Log transaction
├── SELL Signal?
│   ├── Yes → Execute SELL order
│   └── Log transaction
└── HOLD/NO Signal?
    └── Wait for next analysis cycle
```

## 📦 Prerequisites

Before setting up the MT5 Forex Trading Bot, ensure you have the following:

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Internet Connection**: Stable and reliable connection for market data

### Software Requirements
- **MetaTrader 5**: Installed and configured with a trading account
- **Python Package Manager**: pip (included with Python)
- **Virtual Environment**: venv or conda (recommended)

### Account Requirements
- **MT5 Trading Account**: Live or demo account with a broker
- **Sufficient Funds**: Adequate balance for trading (recommended: $1,000+ for demo/live trading)

## 🚀 Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/dreykendrick/mt5-forex-trading-bot.git
cd mt5-forex-trading-bot
```

### Step 2: Create a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure MT5 Connection

1. **Open MetaTrader 5** on your machine
2. **Ensure Terminal is accessible** (if using Python on a different machine, ensure remote access is configured)
3. **Note your account credentials**:
   - Login number
   - Password
   - Server name

### Step 5: Create Configuration File

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

Edit `.env` with your MT5 credentials:

```env
MT5_LOGIN=YOUR_ACCOUNT_LOGIN
MT5_PASSWORD=YOUR_ACCOUNT_PASSWORD
MT5_SERVER=YOUR_BROKER_SERVER
TRADING_PAIRS=EURUSD,GBPUSD,USDJPY
RISK_PERCENTAGE=2.0
DAILY_LOSS_LIMIT=500
```

### Step 6: Validate Configuration

```bash
python scripts/validate_config.py
```

### Step 7: Run the Trading Bot

```bash
python main.py
```

## 📁 Folder Structure

```
mt5-forex-trading-bot/
│
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore configuration
│
├── main.py                            # Entry point for the trading bot
├── config.py                          # Configuration management
│
├── src/                               # Source code directory
│   ├── __init__.py
│   ├── mt5_connector.py               # MT5 API connection handler
│   ├── strategy.py                    # Trading strategy logic
│   ├── indicators.py                  # Technical indicators calculations
│   ├── risk_manager.py                # Risk management and position sizing
│   ├── trade_executor.py              # Trade execution module
│   ├── logger.py                      # Logging and monitoring
│   └── utils.py                       # Utility functions
│
├── strategies/                        # Strategy definitions
│   ├── __init__.py
│   ├── moving_average_strategy.py     # MA-based strategy
│   ├── rsi_strategy.py                # RSI-based strategy
│   ├── macd_strategy.py               # MACD-based strategy
│   └── custom_strategy.py             # Custom hybrid strategy
│
├── data/                              # Data directory
│   ├── market_data/                   # Historical and real-time market data
│   ├── logs/                          # Trading logs and performance records
│   │   ├── trades.log
│   │   ├── errors.log
│   │   └── performance.json
│   └── cache/                         # Temporary data cache
│
├── tests/                             # Unit and integration tests
│   ├── __init__.py
│   ├── test_indicators.py             # Tests for technical indicators
│   ├── test_strategy.py               # Tests for trading strategy
│   ├── test_risk_manager.py           # Tests for risk management
│   └── test_integration.py            # Integration tests
│
├── scripts/                           # Utility scripts
│   ├── __init__.py
│   ├── validate_config.py             # Configuration validation
│   ├── backtest.py                    # Backtesting script
│   ├── generate_report.py             # Performance report generation
│   └── cleanup.py                     # Data cleanup utility
│
├── docs/                              # Documentation
│   ├── SETUP.md                       # Detailed setup guide
│   ├── STRATEGY.md                    # Strategy documentation
│   ├── API.md                         # API reference
│   └── TROUBLESHOOTING.md             # Common issues and solutions
│
└── .github/                           # GitHub configuration
    ├── workflows/                     # CI/CD workflows
    │   └── tests.yml                  # Automated testing pipeline
    └── ISSUE_TEMPLATE/                # Issue templates
        └── bug_report.md
```

### Folder Descriptions

| Folder | Purpose |
|--------|---------|
| `src/` | Core trading bot source code and modules |
| `strategies/` | Different trading strategy implementations |
| `data/` | Market data, logs, and performance metrics |
| `tests/` | Unit and integration test files |
| `scripts/` | Utility scripts for setup, testing, and reporting |
| `docs/` | Comprehensive documentation and guides |
| `.github/` | GitHub-specific configuration (workflows, templates) |

## 📖 Usage Guide

### Basic Trading

```bash
# Start the trading bot with default configuration
python main.py

# Run with specific strategy
python main.py --strategy moving_average

# Run in demo mode (no real trades)
python main.py --demo

# Run with custom configuration
python main.py --config custom_config.json
```

### Backtesting

```bash
# Run backtest for the last 30 days
python scripts/backtest.py --days 30

# Run backtest for a specific date range
python scripts/backtest.py --start 2025-01-01 --end 2025-12-31

# Backtest with specific strategy
python scripts/backtest.py --strategy rsi_strategy --days 60
```

### Generate Performance Report

```bash
# Generate performance report
python scripts/generate_report.py

# Generate report for specific period
python scripts/generate_report.py --start 2025-01-01 --end 2025-12-31
```

## ⚙️ Configuration

### Main Configuration (config.py)

```python
# Strategy Settings
STRATEGY = "moving_average"  # Strategy to use
TIMEFRAME = "M15"            # Candlestick timeframe (M5, M15, H1, D1)

# Risk Management
RISK_PERCENTAGE = 2.0        # Risk per trade as % of account
MAX_DAILY_LOSS = 500         # Maximum daily loss in USD
MAX_POSITIONS = 3            # Maximum concurrent open positions

# Trading Pairs
TRADING_PAIRS = ["EURUSD", "GBPUSD", "USDJPY"]

# Technical Indicators
FAST_MA_PERIOD = 10
SLOW_MA_PERIOD = 20
RSI_PERIOD = 14
RSI_UPPER = 70
RSI_LOWER = 30
```

### Environment Variables (.env)

```env
# MT5 Credentials
MT5_LOGIN=YOUR_LOGIN_NUMBER
MT5_PASSWORD=YOUR_PASSWORD
MT5_SERVER=YOUR_SERVER_NAME

# Trading Settings
TRADING_PAIRS=EURUSD,GBPUSD,USDJPY
RISK_PERCENTAGE=2.0
DAILY_LOSS_LIMIT=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/trading.log

# Development
DEBUG_MODE=False
DEMO_MODE=False
```

## 🛡️ Risk Management

The bot implements multiple layers of risk management:

1. **Position Sizing**: Calculates trade size based on account equity and risk percentage
2. **Stop Loss**: Automatic stop-loss placement to limit losses
3. **Take Profit**: Profit targets based on risk/reward ratio
4. **Daily Loss Limit**: Halts trading if daily losses exceed threshold
5. **Maximum Positions**: Limits concurrent open trades
6. **Margin Check**: Ensures sufficient margin before opening trades

### Risk Formula

```
Position Size = (Account Equity × Risk %) / (Entry Price - Stop Loss) × Lot Size
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/your-feature`)
3. **Make your changes** and add tests
4. **Commit your changes** (`git commit -m 'Add your feature'`)
5. **Push to the branch** (`git push origin feature/your-feature`)
6. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This trading bot is provided for educational and research purposes only.** 

- **Past performance is not indicative of future results**
- **Forex trading carries substantial risk of loss**
- **Use a demo account for testing before trading with real money**
- **The authors are not responsible for any financial losses**
- **Always start with small position sizes when trading live**
- **Regularly monitor the bot and review its performance**

## 📞 Support & Contact

For issues, questions, or suggestions:

- **Open an Issue**: [GitHub Issues](https://github.com/dreykendrick/mt5-forex-trading-bot/issues)
- **Email**: Contact the repository owner
- **Documentation**: Check the [docs/](docs/) folder for detailed guides

---

**Last Updated**: January 14, 2026

**Version**: 1.0.0

**Maintainer**: [dreykendrick](https://github.com/dreykendrick)
