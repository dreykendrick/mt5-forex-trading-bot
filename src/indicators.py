"""
Technical Indicators Module for MT5 Forex Trading Bot

This module provides calculation functions for various technical indicators used in
forex trading analysis including RSI, MACD, Bollinger Bands, Moving Averages, ATR,
Stochastic, and VWAP.

Author: MT5 Forex Trading Bot
Created: 2026-01-14
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional, List
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MACDResult:
    """Data class for MACD calculation results."""
    macd_line: np.ndarray
    signal_line: np.ndarray
    histogram: np.ndarray


@dataclass
class BollingerBandsResult:
    """Data class for Bollinger Bands calculation results."""
    upper_band: np.ndarray
    middle_band: np.ndarray
    lower_band: np.ndarray
    bandwidth: np.ndarray
    percent_b: np.ndarray


@dataclass
class StochasticResult:
    """Data class for Stochastic Oscillator calculation results."""
    k_percent: np.ndarray
    d_percent: np.ndarray


def validate_data(data: Union[list, np.ndarray, pd.Series], 
                  min_length: int = 2, 
                  param_name: str = "data") -> np.ndarray:
    """
    Validate and convert input data to numpy array.
    
    Args:
        data: Input data (list, numpy array, or pandas Series)
        min_length: Minimum required data points
        param_name: Parameter name for error messages
        
    Returns:
        np.ndarray: Validated data as numpy array
        
    Raises:
        ValueError: If data is invalid or insufficient
        TypeError: If data type is not supported
    """
    try:
        if isinstance(data, pd.Series):
            arr = data.values
        elif isinstance(data, (list, tuple)):
            arr = np.array(data, dtype=float)
        elif isinstance(data, np.ndarray):
            arr = data.astype(float)
        else:
            raise TypeError(f"{param_name} must be list, numpy array, or pandas Series")
        
        if len(arr) < min_length:
            raise ValueError(
                f"{param_name} must have at least {min_length} data points, "
                f"got {len(arr)}"
            )
        
        if np.any(np.isnan(arr)):
            logger.warning(f"{param_name} contains NaN values")
        
        return arr
    except Exception as e:
        logger.error(f"Data validation error for {param_name}: {str(e)}")
        raise


def simple_moving_average(data: Union[list, np.ndarray, pd.Series], 
                         period: int = 20) -> np.ndarray:
    """
    Calculate Simple Moving Average (SMA).
    
    The SMA is calculated by taking the arithmetic mean of a given set of prices
    over a specified number of days in the past.
    
    Args:
        data: Price data (list, numpy array, or pandas Series)
        period: Number of periods for calculation (default: 20)
        
    Returns:
        np.ndarray: Array of SMA values, with NaN for insufficient data points
        
    Raises:
        ValueError: If period is invalid or data is insufficient
        
    Example:
        >>> prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        >>> sma = simple_moving_average(prices, period=5)
    """
    try:
        data = validate_data(data, min_length=period, param_name="SMA data")
        
        if period < 1:
            raise ValueError(f"Period must be >= 1, got {period}")
        
        if period > len(data):
            raise ValueError(
                f"Period {period} exceeds data length {len(data)}"
            )
        
        sma = np.convolve(data, np.ones(period) / period, mode='valid')
        
        # Prepend NaN values for alignment
        result = np.concatenate([np.full(period - 1, np.nan), sma])
        
        logger.debug(f"SMA calculated with period={period}, length={len(data)}")
        return result
    except Exception as e:
        logger.error(f"Error calculating SMA: {str(e)}")
        raise


def exponential_moving_average(data: Union[list, np.ndarray, pd.Series], 
                               period: int = 20) -> np.ndarray:
    """
    Calculate Exponential Moving Average (EMA).
    
    The EMA is a weighted moving average that gives more importance to recent prices.
    It responds faster to price changes compared to SMA.
    
    Args:
        data: Price data (list, numpy array, or pandas Series)
        period: Number of periods for calculation (default: 20)
        
    Returns:
        np.ndarray: Array of EMA values
        
    Raises:
        ValueError: If period is invalid or data is insufficient
        
    Example:
        >>> prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        >>> ema = exponential_moving_average(prices, period=5)
    """
    try:
        data = validate_data(data, min_length=period, param_name="EMA data")
        
        if period < 1:
            raise ValueError(f"Period must be >= 1, got {period}")
        
        if period > len(data):
            raise ValueError(
                f"Period {period} exceeds data length {len(data)}"
            )
        
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(data))
        
        # Initialize with SMA of first 'period' values
        ema[period - 1] = np.mean(data[:period])
        
        # Calculate EMA for remaining values
        for i in range(period, len(data)):
            ema[i] = data[i] * multiplier + ema[i - 1] * (1 - multiplier)
        
        # Fill initial values with NaN
        ema[:period - 1] = np.nan
        
        logger.debug(f"EMA calculated with period={period}, length={len(data)}")
        return ema
    except Exception as e:
        logger.error(f"Error calculating EMA: {str(e)}")
        raise


def relative_strength_index(data: Union[list, np.ndarray, pd.Series], 
                            period: int = 14) -> np.ndarray:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI is a momentum oscillator that measures the speed and magnitude of price changes.
    It oscillates between 0 and 100, with values above 70 indicating overbought conditions
    and values below 30 indicating oversold conditions.
    
    Formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
    
    Args:
        data: Price data (list, numpy array, or pandas Series)
        period: Number of periods for calculation (default: 14)
        
    Returns:
        np.ndarray: Array of RSI values (0-100), with NaN for insufficient data
        
    Raises:
        ValueError: If period is invalid or data is insufficient
        
    Example:
        >>> prices = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08]
        >>> rsi = relative_strength_index(prices, period=5)
    """
    try:
        data = validate_data(data, min_length=period + 1, param_name="RSI data")
        
        if period < 1:
            raise ValueError(f"Period must be >= 1, got {period}")
        
        # Calculate price changes
        deltas = np.diff(data)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Initialize arrays
        rsi = np.zeros(len(data))
        rsi[:period] = np.nan
        
        # Calculate average gains and losses using EMA method
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(data)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi[i] = 100 if avg_gain > 0 else 0
            else:
                rs = avg_gain / avg_loss
                rsi[i] = 100 - (100 / (1 + rs))
        
        logger.debug(f"RSI calculated with period={period}, length={len(data)}")
        return rsi
    except Exception as e:
        logger.error(f"Error calculating RSI: {str(e)}")
        raise


def moving_average_convergence_divergence(
    data: Union[list, np.ndarray, pd.Series],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> MACDResult:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    MACD is a trend-following momentum indicator that shows the relationship between
    two moving averages of prices. It consists of the MACD line, signal line, and
    histogram (difference between MACD and signal line).
    
    Formula:
        MACD Line = EMA(12) - EMA(26)
        Signal Line = EMA(MACD Line, 9)
        Histogram = MACD Line - Signal Line
    
    Args:
        data: Price data (list, numpy array, or pandas Series)
        fast_period: Period for fast EMA (default: 12)
        slow_period: Period for slow EMA (default: 26)
        signal_period: Period for signal line EMA (default: 9)
        
    Returns:
        MACDResult: Dataclass containing macd_line, signal_line, and histogram
        
    Raises:
        ValueError: If periods are invalid or data is insufficient
        
    Example:
        >>> prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
        >>> macd = moving_average_convergence_divergence(prices)
        >>> print(macd.macd_line, macd.signal_line, macd.histogram)
    """
    try:
        data = validate_data(data, min_length=slow_period + 1, param_name="MACD data")
        
        if fast_period < 1 or slow_period < 1 or signal_period < 1:
            raise ValueError("All periods must be >= 1")
        
        if fast_period >= slow_period:
            raise ValueError(
                f"Fast period {fast_period} must be less than slow period {slow_period}"
            )
        
        # Calculate EMAs
        ema_fast = exponential_moving_average(data, fast_period)
        ema_slow = exponential_moving_average(data, slow_period)
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD line)
        # Remove NaN values for signal line calculation
        valid_macd = macd_line[~np.isnan(macd_line)]
        
        if len(valid_macd) < signal_period:
            logger.warning(f"Not enough valid MACD values for signal calculation")
            signal_line = np.full_like(macd_line, np.nan)
        else:
            signal_ema = exponential_moving_average(valid_macd, signal_period)
            signal_line = np.full_like(macd_line, np.nan)
            signal_line[-len(signal_ema):] = signal_ema
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        logger.debug(
            f"MACD calculated with fast={fast_period}, slow={slow_period}, "
            f"signal={signal_period}, length={len(data)}"
        )
        return MACDResult(macd_line=macd_line, signal_line=signal_line, 
                         histogram=histogram)
    except Exception as e:
        logger.error(f"Error calculating MACD: {str(e)}")
        raise


def bollinger_bands(data: Union[list, np.ndarray, pd.Series],
                   period: int = 20,
                   num_std_dev: float = 2.0) -> BollingerBandsResult:
    """
    Calculate Bollinger Bands.
    
    Bollinger Bands consist of a middle band (SMA) and two outer bands placed at
    a specified number of standard deviations away from the middle band. They are
    used to identify overbought/oversold conditions and potential price reversals.
    
    Formula:
        Middle Band = SMA(period)
        Upper Band = SMA + (std_dev * num_std_dev)
        Lower Band = SMA - (std_dev * num_std_dev)
        Bandwidth = (Upper Band - Lower Band) / Middle Band
        Percent B = (Price - Lower Band) / (Upper Band - Lower Band)
    
    Args:
        data: Price data (list, numpy array, or pandas Series)
        period: Number of periods for SMA calculation (default: 20)
        num_std_dev: Number of standard deviations (default: 2.0)
        
    Returns:
        BollingerBandsResult: Dataclass containing upper_band, middle_band,
                             lower_band, bandwidth, and percent_b arrays
        
    Raises:
        ValueError: If period is invalid or data is insufficient
        
    Example:
        >>> prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        >>> bb = bollinger_bands(prices, period=5, num_std_dev=2.0)
        >>> print(bb.upper_band, bb.lower_band)
    """
    try:
        data = validate_data(data, min_length=period, param_name="Bollinger Bands data")
        
        if period < 1:
            raise ValueError(f"Period must be >= 1, got {period}")
        
        if num_std_dev <= 0:
            raise ValueError(f"Number of std dev must be > 0, got {num_std_dev}")
        
        # Calculate middle band (SMA)
        middle_band = simple_moving_average(data, period)
        
        # Calculate standard deviation
        std_dev = np.full_like(data, np.nan, dtype=float)
        for i in range(period - 1, len(data)):
            std_dev[i] = np.std(data[i - period + 1:i + 1], ddof=1)
        
        # Calculate bands
        upper_band = middle_band + (std_dev * num_std_dev)
        lower_band = middle_band - (std_dev * num_std_dev)
        
        # Calculate bandwidth
        bandwidth = np.full_like(data, np.nan, dtype=float)
        valid_mask = ~np.isnan(upper_band) & ~np.isnan(lower_band) & \
                     ~np.isnan(middle_band) & (middle_band != 0)
        bandwidth[valid_mask] = (upper_band[valid_mask] - lower_band[valid_mask]) / \
                                middle_band[valid_mask]
        
        # Calculate Percent B
        percent_b = np.full_like(data, np.nan, dtype=float)
        valid_mask = ~np.isnan(upper_band) & ~np.isnan(lower_band) & \
                     (upper_band - lower_band != 0)
        percent_b[valid_mask] = (data[valid_mask] - lower_band[valid_mask]) / \
                               (upper_band[valid_mask] - lower_band[valid_mask])
        
        logger.debug(
            f"Bollinger Bands calculated with period={period}, "
            f"std_dev={num_std_dev}, length={len(data)}"
        )
        return BollingerBandsResult(
            upper_band=upper_band,
            middle_band=middle_band,
            lower_band=lower_band,
            bandwidth=bandwidth,
            percent_b=percent_b
        )
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {str(e)}")
        raise


def average_true_range(high: Union[list, np.ndarray, pd.Series],
                      low: Union[list, np.ndarray, pd.Series],
                      close: Union[list, np.ndarray, pd.Series],
                      period: int = 14) -> np.ndarray:
    """
    Calculate Average True Range (ATR).
    
    ATR measures market volatility by calculating the average of true ranges over
    a specified period. It helps traders determine appropriate stop-loss and
    take-profit levels.
    
    Formula:
        True Range = max(High - Low, |High - Close_prev|, |Low - Close_prev|)
        ATR = EMA(True Range, period)
    
    Args:
        high: High prices (list, numpy array, or pandas Series)
        low: Low prices (list, numpy array, or pandas Series)
        close: Close prices (list, numpy array, or pandas Series)
        period: Number of periods for EMA calculation (default: 14)
        
    Returns:
        np.ndarray: Array of ATR values, with NaN for insufficient data
        
    Raises:
        ValueError: If data lengths don't match or period is invalid
        
    Example:
        >>> high = [10.5, 11.0, 11.5, 12.0, 12.5]
        >>> low = [9.5, 10.0, 10.5, 11.0, 11.5]
        >>> close = [10.0, 10.5, 11.0, 11.5, 12.0]
        >>> atr = average_true_range(high, low, close, period=3)
    """
    try:
        high = validate_data(high, min_length=period + 1, param_name="ATR high")
        low = validate_data(low, min_length=period + 1, param_name="ATR low")
        close = validate_data(close, min_length=period + 1, param_name="ATR close")
        
        if not (len(high) == len(low) == len(close)):
            raise ValueError(
                f"High, Low, and Close arrays must have same length. "
                f"Got {len(high)}, {len(low)}, {len(close)}"
            )
        
        if period < 1:
            raise ValueError(f"Period must be >= 1, got {period}")
        
        # Calculate true range
        tr = np.zeros(len(high))
        tr[0] = high[0] - low[0]
        
        for i in range(1, len(high)):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )
        
        # Calculate ATR using EMA
        atr = exponential_moving_average(tr, period)
        
        logger.debug(f"ATR calculated with period={period}, length={len(high)}")
        return atr
    except Exception as e:
        logger.error(f"Error calculating ATR: {str(e)}")
        raise


def stochastic_oscillator(high: Union[list, np.ndarray, pd.Series],
                         low: Union[list, np.ndarray, pd.Series],
                         close: Union[list, np.ndarray, pd.Series],
                         period: int = 14,
                         smooth_k: int = 3,
                         smooth_d: int = 3) -> StochasticResult:
    """
    Calculate Stochastic Oscillator.
    
    The Stochastic Oscillator is a momentum indicator that compares a closing price
    to a price range over a specific period. It generates values between 0 and 100
    and helps identify overbought/oversold conditions. %K represents the raw stochastic,
    and %D is a moving average of %K.
    
    Formula:
        %K = 100 * ((Close - Lowest Low) / (Highest High - Lowest Low))
        %D = SMA(%K, smooth_d)
    
    Args:
        high: High prices (list, numpy array, or pandas Series)
        low: Low prices (list, numpy array, or pandas Series)
        close: Close prices (list, numpy array, or pandas Series)
        period: Number of periods for min/max calculation (default: 14)
        smooth_k: Period for smoothing %K (default: 3)
        smooth_d: Period for smoothing %D (default: 3)
        
    Returns:
        StochasticResult: Dataclass containing k_percent and d_percent arrays
        
    Raises:
        ValueError: If data lengths don't match or periods are invalid
        
    Example:
        >>> high = [10.5, 11.0, 11.5, 12.0, 12.5]
        >>> low = [9.5, 10.0, 10.5, 11.0, 11.5]
        >>> close = [10.0, 10.5, 11.0, 11.5, 12.0]
        >>> stoch = stochastic_oscillator(high, low, close, period=3)
        >>> print(stoch.k_percent, stoch.d_percent)
    """
    try:
        high = validate_data(high, min_length=period, param_name="Stochastic high")
        low = validate_data(low, min_length=period, param_name="Stochastic low")
        close = validate_data(close, min_length=period, param_name="Stochastic close")
        
        if not (len(high) == len(low) == len(close)):
            raise ValueError(
                f"High, Low, and Close arrays must have same length. "
                f"Got {len(high)}, {len(low)}, {len(close)}"
            )
        
        if period < 1:
            raise ValueError(f"Period must be >= 1, got {period}")
        
        if smooth_k < 1 or smooth_d < 1:
            raise ValueError("Smooth K and D periods must be >= 1")
        
        # Calculate raw %K
        k_raw = np.zeros(len(close))
        k_raw[:period - 1] = np.nan
        
        for i in range(period - 1, len(close)):
            lowest_low = np.min(low[i - period + 1:i + 1])
            highest_high = np.max(high[i - period + 1:i + 1])
            
            denominator = highest_high - lowest_low
            if denominator == 0:
                k_raw[i] = 50  # Neutral value when no range
            else:
                k_raw[i] = 100 * (close[i] - lowest_low) / denominator
        
        # Smooth %K using SMA
        valid_k = k_raw[~np.isnan(k_raw)]
        if len(valid_k) >= smooth_k:
            smoothed_k = simple_moving_average(valid_k, smooth_k)
            k_percent = np.full_like(k_raw, np.nan, dtype=float)
            k_percent[-len(smoothed_k):] = smoothed_k
        else:
            logger.warning("Not enough valid %K values for smoothing")
            k_percent = k_raw
        
        # Calculate %D (EMA of smoothed %K)
        valid_k_smooth = k_percent[~np.isnan(k_percent)]
        if len(valid_k_smooth) >= smooth_d:
            d_percent_temp = exponential_moving_average(valid_k_smooth, smooth_d)
            d_percent = np.full_like(k_percent, np.nan, dtype=float)
            d_percent[-len(d_percent_temp):] = d_percent_temp
        else:
            logger.warning("Not enough valid smoothed %K values for %D calculation")
            d_percent = np.full_like(k_percent, np.nan, dtype=float)
        
        logger.debug(
            f"Stochastic calculated with period={period}, "
            f"smooth_k={smooth_k}, smooth_d={smooth_d}, length={len(high)}"
        )
        return StochasticResult(k_percent=k_percent, d_percent=d_percent)
    except Exception as e:
        logger.error(f"Error calculating Stochastic: {str(e)}")
        raise


def volume_weighted_average_price(high: Union[list, np.ndarray, pd.Series],
                                 low: Union[list, np.ndarray, pd.Series],
                                 close: Union[list, np.ndarray, pd.Series],
                                 volume: Union[list, np.ndarray, pd.Series]) -> np.ndarray:
    """
    Calculate Volume Weighted Average Price (VWAP).
    
    VWAP is a trading benchmark that shows the average price a security has traded
    at throughout the day, weighted by volume. It's calculated from the opening of
    the market and updated throughout the trading session.
    
    Formula:
        Typical Price = (High + Low + Close) / 3
        VWAP = Cumulative(Typical Price * Volume) / Cumulative(Volume)
    
    Args:
        high: High prices (list, numpy array, or pandas Series)
        low: Low prices (list, numpy array, or pandas Series)
        close: Close prices (list, numpy array, or pandas Series)
        volume: Trading volumes (list, numpy array, or pandas Series)
        
    Returns:
        np.ndarray: Array of VWAP values
        
    Raises:
        ValueError: If data lengths don't match or data is invalid
        
    Example:
        >>> high = [10.5, 11.0, 11.5, 12.0, 12.5]
        >>> low = [9.5, 10.0, 10.5, 11.0, 11.5]
        >>> close = [10.0, 10.5, 11.0, 11.5, 12.0]
        >>> volume = [1000, 1500, 1200, 1800, 1400]
        >>> vwap = volume_weighted_average_price(high, low, close, volume)
    """
    try:
        high = validate_data(high, min_length=1, param_name="VWAP high")
        low = validate_data(low, min_length=1, param_name="VWAP low")
        close = validate_data(close, min_length=1, param_name="VWAP close")
        volume = validate_data(volume, min_length=1, param_name="VWAP volume")
        
        if not (len(high) == len(low) == len(close) == len(volume)):
            raise ValueError(
                f"High, Low, Close, and Volume arrays must have same length. "
                f"Got {len(high)}, {len(low)}, {len(close)}, {len(volume)}"
            )
        
        if np.any(volume <= 0):
            logger.warning("Volume contains zero or negative values")
        
        # Calculate typical price
        typical_price = (high + low + close) / 3
        
        # Calculate VWAP
        vwap = np.zeros(len(close))
        cumulative_tp_vol = 0
        cumulative_vol = 0
        
        for i in range(len(close)):
            cumulative_tp_vol += typical_price[i] * volume[i]
            cumulative_vol += volume[i]
            
            if cumulative_vol > 0:
                vwap[i] = cumulative_tp_vol / cumulative_vol
            else:
                vwap[i] = np.nan
        
        logger.debug(f"VWAP calculated with length={len(high)}")
        return vwap
    except Exception as e:
        logger.error(f"Error calculating VWAP: {str(e)}")
        raise


def get_indicator_summary(data: pd.DataFrame, 
                         symbol: str = "EURUSD") -> dict:
    """
    Calculate all indicators for a given dataset and return a summary.
    
    This convenience function calculates all available technical indicators
    for a given price data and returns a dictionary with results.
    
    Args:
        data: DataFrame with columns 'open', 'high', 'low', 'close', 'volume'
        symbol: Symbol name for logging (default: "EURUSD")
        
    Returns:
        dict: Dictionary containing all calculated indicators
        
    Raises:
        ValueError: If required columns are missing
        
    Example:
        >>> df = pd.DataFrame({
        ...     'open': [10, 11, 12],
        ...     'high': [10.5, 11.5, 12.5],
        ...     'low': [9.5, 10.5, 11.5],
        ...     'close': [10.2, 11.2, 12.2],
        ...     'volume': [1000, 1500, 1200]
        ... })
        >>> summary = get_indicator_summary(df, symbol="EURUSD")
    """
    try:
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        logger.info(f"Calculating indicators for {symbol}")
        
        # Moving Averages
        sma_20 = simple_moving_average(data['close'], 20)
        sma_50 = simple_moving_average(data['close'], 50)
        ema_12 = exponential_moving_average(data['close'], 12)
        ema_26 = exponential_moving_average(data['close'], 26)
        
        # RSI
        rsi_14 = relative_strength_index(data['close'], 14)
        
        # MACD
        macd = moving_average_convergence_divergence(data['close'])
        
        # Bollinger Bands
        bb = bollinger_bands(data['close'], 20, 2.0)
        
        # ATR
        atr_14 = average_true_range(data['high'], data['low'], data['close'], 14)
        
        # Stochastic
        stoch = stochastic_oscillator(data['high'], data['low'], data['close'])
        
        # VWAP
        vwap = volume_weighted_average_price(
            data['high'], data['low'], data['close'], data['volume']
        )
        
        summary = {
            'symbol': symbol,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_12': ema_12,
            'ema_26': ema_26,
            'rsi_14': rsi_14,
            'macd': macd,
            'bollinger_bands': bb,
            'atr_14': atr_14,
            'stochastic': stoch,
            'vwap': vwap
        }
        
        logger.info(f"Indicators calculated successfully for {symbol}")
        return summary
    except Exception as e:
        logger.error(f"Error calculating indicator summary for {symbol}: {str(e)}")
        raise
