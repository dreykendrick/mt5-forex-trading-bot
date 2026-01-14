"""
Risk Manager Module for MT5 Forex Trading Bot

This module handles all risk management calculations including:
- Position sizing based on account risk
- Stop loss and take profit level calculations
- Risk-to-reward ratio calculations
- Maximum position sizing constraints
- Account equity management
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Dict
import math

# Configure logging
logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Enumeration for order types"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class RiskParameters:
    """Data class for risk management parameters"""
    account_balance: float
    risk_percentage: float  # Percentage of account to risk per trade (e.g., 2.0 for 2%)
    max_position_size: float  # Maximum position size in lots
    min_position_size: float  # Minimum position size in lots
    pip_value: float  # Value per pip for the currency pair
    leverage: int = 1  # Account leverage


@dataclass
class PositionSizing:
    """Data class for position sizing calculations"""
    position_size: float  # Size in lots
    risk_amount: float  # Amount at risk in account currency
    stop_loss_pips: float  # Stop loss in pips
    entry_price: float  # Entry price
    stop_loss_price: float  # Stop loss price level
    take_profit_price: float  # Take profit price level
    risk_reward_ratio: float  # Risk to reward ratio
    potential_profit: float  # Potential profit amount


class RiskManager:
    """
    Manages all risk-related calculations for forex trading
    """

    def __init__(self, account_balance: float, risk_percentage: float = 2.0,
                 max_position_size: float = 10.0, min_position_size: float = 0.01,
                 leverage: int = 1):
        """
        Initialize Risk Manager

        Args:
            account_balance: Initial account balance in account currency
            risk_percentage: Percentage of account to risk per trade (default: 2%)
            max_position_size: Maximum allowed position size in lots (default: 10)
            min_position_size: Minimum allowed position size in lots (default: 0.01)
            leverage: Account leverage (default: 1)
        """
        self.account_balance = account_balance
        self.risk_percentage = risk_percentage
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.leverage = leverage
        self.current_equity = account_balance
        self.trades_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0

        logger.info(f"Risk Manager initialized - Balance: {account_balance}, "
                    f"Risk: {risk_percentage}%, Leverage: {leverage}x")

    def update_equity(self, current_equity: float) -> None:
        """
        Update current account equity

        Args:
            current_equity: Current account equity/balance
        """
        self.current_equity = current_equity
        logger.debug(f"Equity updated to: {current_equity}")

    def calculate_position_size(self, entry_price: float, stop_loss_price: float,
                               pip_value: float) -> float:
        """
        Calculate position size based on risk management rules

        Args:
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price level
            pip_value: Value per pip for the currency pair

        Returns:
            Position size in lots
        """
        if entry_price == stop_loss_price:
            logger.warning("Entry price and stop loss price are identical")
            return self.min_position_size

        # Calculate stop loss distance in pips
        stop_loss_pips = abs(entry_price - stop_loss_price) / (pip_value / 100)

        # Calculate risk amount in account currency
        risk_amount = (self.current_equity * self.risk_percentage) / 100

        # Calculate position size
        # Position Size = Risk Amount / (Stop Loss Pips * Pip Value)
        position_size = risk_amount / (stop_loss_pips * pip_value)

        # Apply constraints
        position_size = max(self.min_position_size, min(position_size, self.max_position_size))

        logger.debug(f"Position size calculated: {position_size} lots, "
                    f"Risk: {risk_amount}, SL Pips: {stop_loss_pips}")

        return round(position_size, 2)

    def calculate_stop_loss_level(self, entry_price: float, order_type: OrderType,
                                 stop_loss_pips: float, pip_value: float) -> float:
        """
        Calculate stop loss price level

        Args:
            entry_price: Entry price for the trade
            order_type: Type of order (BUY or SELL)
            stop_loss_pips: Stop loss distance in pips
            pip_value: Value per pip for the currency pair

        Returns:
            Stop loss price level
        """
        stop_loss_distance = (stop_loss_pips * pip_value) / 100

        if order_type == OrderType.BUY:
            stop_loss_price = entry_price - stop_loss_distance
        else:  # SELL
            stop_loss_price = entry_price + stop_loss_distance

        logger.debug(f"Stop loss calculated: {stop_loss_price} "
                    f"({stop_loss_pips} pips from entry)")

        return round(stop_loss_price, 5)

    def calculate_take_profit_level(self, entry_price: float, order_type: OrderType,
                                   take_profit_pips: float, pip_value: float) -> float:
        """
        Calculate take profit price level

        Args:
            entry_price: Entry price for the trade
            order_type: Type of order (BUY or SELL)
            take_profit_pips: Take profit distance in pips
            pip_value: Value per pip for the currency pair

        Returns:
            Take profit price level
        """
        take_profit_distance = (take_profit_pips * pip_value) / 100

        if order_type == OrderType.BUY:
            take_profit_price = entry_price + take_profit_distance
        else:  # SELL
            take_profit_price = entry_price - take_profit_distance

        logger.debug(f"Take profit calculated: {take_profit_price} "
                    f"({take_profit_pips} pips from entry)")

        return round(take_profit_price, 5)

    def calculate_risk_reward_ratio(self, stop_loss_pips: float,
                                   take_profit_pips: float) -> float:
        """
        Calculate risk-to-reward ratio

        Args:
            stop_loss_pips: Stop loss distance in pips
            take_profit_pips: Take profit distance in pips

        Returns:
            Risk-to-reward ratio
        """
        if stop_loss_pips == 0:
            logger.warning("Stop loss pips cannot be zero")
            return 0.0

        ratio = take_profit_pips / stop_loss_pips

        logger.debug(f"Risk-reward ratio calculated: 1:{ratio:.2f}")

        return round(ratio, 2)

    def calculate_complete_position(self, entry_price: float, stop_loss_pips: float,
                                   take_profit_pips: float, order_type: OrderType,
                                   pip_value: float) -> PositionSizing:
        """
        Calculate complete position details including sizing, S/L, T/P, and R/R

        Args:
            entry_price: Entry price for the trade
            stop_loss_pips: Stop loss distance in pips
            take_profit_pips: Take profit distance in pips
            order_type: Type of order (BUY or SELL)
            pip_value: Value per pip for the currency pair

        Returns:
            PositionSizing object with all calculations
        """
        # Calculate stop loss and take profit levels
        stop_loss_price = self.calculate_stop_loss_level(
            entry_price, order_type, stop_loss_pips, pip_value
        )
        take_profit_price = self.calculate_take_profit_level(
            entry_price, order_type, take_profit_pips, pip_value
        )

        # Calculate position size
        position_size = self.calculate_position_size(
            entry_price, stop_loss_price, pip_value
        )

        # Calculate risk and reward amounts
        risk_amount = (self.current_equity * self.risk_percentage) / 100
        potential_profit = (position_size * take_profit_pips * pip_value)

        # Calculate risk-reward ratio
        risk_reward_ratio = self.calculate_risk_reward_ratio(
            stop_loss_pips, take_profit_pips
        )

        position = PositionSizing(
            position_size=position_size,
            risk_amount=round(risk_amount, 2),
            stop_loss_pips=stop_loss_pips,
            entry_price=entry_price,
            stop_loss_price=round(stop_loss_price, 5),
            take_profit_price=round(take_profit_price, 5),
            risk_reward_ratio=risk_reward_ratio,
            potential_profit=round(potential_profit, 2)
        )

        logger.info(f"Complete position calculated - Size: {position_size} lots, "
                   f"Risk: {risk_amount}, R/R: 1:{risk_reward_ratio}")

        return position

    def validate_position(self, position: PositionSizing, min_rr_ratio: float = 1.0) -> Tuple[bool, str]:
        """
        Validate if a position meets risk management criteria

        Args:
            position: PositionSizing object to validate
            min_rr_ratio: Minimum acceptable risk-reward ratio (default: 1.0)

        Returns:
            Tuple of (is_valid, message)
        """
        errors = []

        # Check position size
        if position.position_size < self.min_position_size:
            errors.append(f"Position size {position.position_size} below minimum {self.min_position_size}")
        if position.position_size > self.max_position_size:
            errors.append(f"Position size {position.position_size} exceeds maximum {self.max_position_size}")

        # Check risk-reward ratio
        if position.risk_reward_ratio < min_rr_ratio:
            errors.append(f"Risk-reward ratio {position.risk_reward_ratio} below minimum {min_rr_ratio}")

        # Check stop loss and entry price are different
        if position.entry_price == position.stop_loss_price:
            errors.append("Entry price cannot equal stop loss price")

        # Check take profit and entry price are different
        if position.entry_price == position.take_profit_price:
            errors.append("Entry price cannot equal take profit price")

        if errors:
            message = "; ".join(errors)
            logger.warning(f"Position validation failed: {message}")
            return False, message

        logger.info("Position validation passed")
        return True, "Position is valid"

    def calculate_max_position_by_equity(self, equity_percentage: float) -> float:
        """
        Calculate maximum position size based on equity percentage

        Args:
            equity_percentage: Percentage of equity to allocate (e.g., 5.0 for 5%)

        Returns:
            Maximum position size in lots
        """
        # Account for leverage
        max_position = (self.current_equity * equity_percentage / 100) * self.leverage

        logger.debug(f"Max position by equity: {max_position} lots ({equity_percentage}% equity)")

        return round(max_position, 2)

    def calculate_pip_value(self, pair: str, account_currency: str = "USD") -> float:
        """
        Calculate pip value for a currency pair
        Note: This is a simplified calculation. Real implementation should use
        MT5 API to get accurate pip values.

        Args:
            pair: Currency pair (e.g., "EURUSD")
            account_currency: Account currency (default: "USD")

        Returns:
            Pip value for the pair
        """
        # For major pairs with USD as quote currency
        if pair.endswith("USD"):
            return 0.0001  # 1 pip = 0.0001

        # For pairs with other quote currencies
        if pair.endswith("JPY"):
            return 0.01  # 1 pip = 0.01

        # Default to 4 decimals (0.0001)
        return 0.0001

    def record_trade_result(self, profit_loss: float) -> None:
        """
        Record the result of a completed trade for statistics

        Args:
            profit_loss: Profit or loss from the trade
        """
        self.trades_count += 1
        self.total_profit += profit_loss

        if profit_loss > 0:
            self.winning_trades += 1
        elif profit_loss < 0:
            self.losing_trades += 0
        else:
            # Break-even trades counted as partial win
            self.winning_trades += 0.5

        logger.info(f"Trade recorded - P/L: {profit_loss}, "
                   f"Total: {self.total_profit}, Win Rate: {self.get_win_rate():.2f}%")

    def get_win_rate(self) -> float:
        """
        Calculate win rate percentage

        Returns:
            Win rate as percentage
        """
        if self.trades_count == 0:
            return 0.0

        return (self.winning_trades / self.trades_count) * 100

    def get_statistics(self) -> Dict:
        """
        Get trading statistics

        Returns:
            Dictionary with trading statistics
        """
        stats = {
            "total_trades": self.trades_count,
            "winning_trades": int(self.winning_trades),
            "losing_trades": self.losing_trades,
            "win_rate": round(self.get_win_rate(), 2),
            "total_profit": round(self.total_profit, 2),
            "current_equity": round(self.current_equity, 2),
            "account_balance": round(self.account_balance, 2),
            "total_return": round((self.total_profit / self.account_balance) * 100, 2),
        }

        logger.debug(f"Statistics: {stats}")

        return stats

    def reset_statistics(self) -> None:
        """Reset all trading statistics"""
        self.trades_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        logger.info("Statistics reset")

    def __repr__(self) -> str:
        """String representation of RiskManager"""
        return (f"RiskManager(balance={self.current_equity}, "
                f"risk={self.risk_percentage}%, "
                f"trades={self.trades_count}, "
                f"win_rate={self.get_win_rate():.2f}%)")
