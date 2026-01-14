"""
MT5 Connector Module

This module provides a comprehensive wrapper around the MetaTrader 5 Python library,
managing connections, authentication, and various trading operations with robust
error handling and logging.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any

try:
    import MetaTrader5 as mt5
except ImportError:
    raise ImportError("MetaTrader5 library is required. Install it using: pip install MetaTrader5")

import pandas as pd


class MT5ConnectionError(Exception):
    """Custom exception for MT5 connection errors"""
    pass


class MT5AuthenticationError(Exception):
    """Custom exception for MT5 authentication errors"""
    pass


class MT5OperationError(Exception):
    """Custom exception for MT5 operation errors"""
    pass


class MT5Connector:
    """
    MT5Connector manages MetaTrader 5 connections and API interactions.
    
    This class provides a unified interface for:
    - Establishing and managing MT5 connections
    - User authentication
    - Account information retrieval
    - Symbol data and market information
    - Historical OHLC data fetching
    - Order placement and management
    - Position management
    """

    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the MT5Connector.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Raises:
            ImportError: If MetaTrader5 library is not installed
        """
        self.logger = self._setup_logging(log_level)
        self.is_connected = False
        self.account_info = None
        self.logger.info("MT5Connector initialized")

    def _setup_logging(self, log_level: str) -> logging.Logger:
        """
        Configure logging for the connector.
        
        Args:
            log_level: Logging level as string
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(__name__)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Set log level
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(numeric_level)
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(numeric_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(ch)
        
        return logger

    def connect(self, path: Optional[str] = None) -> bool:
        """
        Establish connection to MetaTrader 5 terminal.
        
        Args:
            path: Optional path to the MT5 terminal executable.
                  If None, MT5 will use the default installation path.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            MT5ConnectionError: If connection fails
        """
        try:
            self.logger.info("Attempting to connect to MetaTrader 5...")
            
            if path:
                if not mt5.initialize(path=path):
                    error_msg = f"Failed to initialize MT5 with path: {path}"
                    self.logger.error(error_msg)
                    raise MT5ConnectionError(error_msg)
            else:
                if not mt5.initialize():
                    error_msg = "Failed to initialize MT5"
                    self.logger.error(error_msg)
                    raise MT5ConnectionError(error_msg)
            
            self.is_connected = True
            self.logger.info("Successfully connected to MetaTrader 5")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise MT5ConnectionError(f"Failed to connect to MT5: {str(e)}")

    def login(self, login: int, password: str, server: str) -> bool:
        """
        Authenticate with MetaTrader 5 account.
        
        Args:
            login: Account login number
            password: Account password
            server: Server name (e.g., "MetaQuotes-Demo" or "XM.COM-Demo")
        
        Returns:
            True if login successful, False otherwise
            
        Raises:
            MT5ConnectionError: If not connected to MT5
            MT5AuthenticationError: If authentication fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5. Call connect() first.")
            
            self.logger.info(f"Attempting login with account: {login}")
            
            if not mt5.login(login=login, password=password, server=server):
                error_msg = f"Authentication failed for login {login} on server {server}"
                self.logger.error(error_msg)
                raise MT5AuthenticationError(error_msg)
            
            # Fetch and store account info
            self.account_info = mt5.account_info()
            if not self.account_info:
                raise MT5AuthenticationError("Failed to retrieve account information after login")
            
            self.logger.info(
                f"Successfully logged in. Account: {self.account_info.name}, "
                f"Balance: {self.account_info.balance}"
            )
            return True
            
        except (MT5ConnectionError, MT5AuthenticationError):
            raise
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            raise MT5AuthenticationError(f"Login failed: {str(e)}")

    def disconnect(self) -> bool:
        """
        Close the connection to MetaTrader 5.
        
        Returns:
            True if disconnection successful
        """
        try:
            self.logger.info("Disconnecting from MetaTrader 5...")
            mt5.shutdown()
            self.is_connected = False
            self.logger.info("Successfully disconnected from MetaTrader 5")
            return True
        except Exception as e:
            self.logger.error(f"Disconnection error: {str(e)}")
            return False

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve current account information.
        
        Returns:
            Dictionary containing account details or None if failed
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            account_info = mt5.account_info()
            if not account_info:
                raise MT5OperationError("Failed to retrieve account information")
            
            self.account_info = account_info
            
            account_dict = {
                'login': account_info.login,
                'name': account_info.name,
                'server': account_info.server,
                'currency': account_info.currency,
                'balance': account_info.balance,
                'credit': account_info.credit,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'leverage': account_info.leverage,
                'profit': account_info.profit,
                'commission': account_info.commission,
            }
            
            self.logger.debug(f"Retrieved account info: {account_dict}")
            return account_dict
            
        except MT5ConnectionError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving account info: {str(e)}")
            raise MT5OperationError(f"Failed to get account info: {str(e)}")

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve symbol information and trading parameters.
        
        Args:
            symbol: Symbol name (e.g., "EURUSD")
        
        Returns:
            Dictionary containing symbol information or None if failed
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                self.logger.warning(f"Symbol {symbol} not found")
                return None
            
            symbol_dict = {
                'symbol': symbol_info.name,
                'description': symbol_info.description,
                'bid': symbol_info.bid,
                'ask': symbol_info.ask,
                'volume': symbol_info.volume,
                'volume_high': symbol_info.volumehigh,
                'volume_low': symbol_info.volumelow,
                'time': symbol_info.time,
                'digits': symbol_info.digits,
                'spread': symbol_info.spread,
                'spread_real': symbol_info.spread_real,
                'trade_mode': symbol_info.trade_mode,
                'min_volume': symbol_info.volume_min,
                'max_volume': symbol_info.volume_max,
                'step': symbol_info.volume_step,
                'tick_size': symbol_info.point,
                'tick_value': symbol_info.trade_tick_value,
            }
            
            self.logger.debug(f"Retrieved symbol info for {symbol}: bid={symbol_info.bid}, ask={symbol_info.ask}")
            return symbol_dict
            
        except MT5ConnectionError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving symbol info for {symbol}: {str(e)}")
            raise MT5OperationError(f"Failed to get symbol info for {symbol}: {str(e)}")

    def get_ohlc_data(
        self,
        symbol: str,
        timeframe: str,
        count: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Retrieve historical OHLC (Open, High, Low, Close) data for a symbol.
        
        Args:
            symbol: Symbol name (e.g., "EURUSD")
            timeframe: Timeframe string ("M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1")
            count: Number of candles to retrieve (default: 100, alternative to start_time/end_time)
            start_time: Start datetime for data range
            end_time: End datetime for data range
        
        Returns:
            DataFrame with OHLC data or None if failed
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            # Map timeframe strings to mt5 constants
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1,
                'W1': mt5.TIMEFRAME_W1,
                'MN1': mt5.TIMEFRAME_MN1,
            }
            
            if timeframe not in timeframe_map:
                raise ValueError(f"Invalid timeframe: {timeframe}. Must be one of {list(timeframe_map.keys())}")
            
            mt5_timeframe = timeframe_map[timeframe]
            
            self.logger.info(f"Fetching {timeframe} OHLC data for {symbol}...")
            
            # Fetch data based on provided parameters
            if count:
                bars = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            elif start_time and end_time:
                bars = mt5.copy_rates_range(symbol, mt5_timeframe, start_time, end_time)
            elif start_time:
                bars = mt5.copy_rates_from(symbol, mt5_timeframe, start_time, 1000)
            else:
                # Default to last 100 candles
                bars = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, 100)
            
            if bars is None or len(bars) == 0:
                self.logger.warning(f"No data retrieved for {symbol} on {timeframe} timeframe")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(bars)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Rename columns for clarity
            df.rename(columns={
                'time': 'time',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'tick_volume': 'volume',
                'real_volume': 'real_volume',
                'spread': 'spread'
            }, inplace=True)
            
            # Reorder columns
            df = df[['time', 'open', 'high', 'low', 'close', 'volume', 'real_volume', 'spread']]
            
            self.logger.info(f"Retrieved {len(df)} bars for {symbol} on {timeframe} timeframe")
            return df
            
        except MT5ConnectionError:
            raise
        except ValueError as e:
            self.logger.error(f"Invalid parameter: {str(e)}")
            raise MT5OperationError(str(e))
        except Exception as e:
            self.logger.error(f"Error retrieving OHLC data for {symbol}: {str(e)}")
            raise MT5OperationError(f"Failed to get OHLC data for {symbol}: {str(e)}")

    def place_order(
        self,
        symbol: str,
        order_type: str,
        volume: float,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "MT5Connector Order"
    ) -> Optional[Dict[str, Any]]:
        """
        Place a new order.
        
        Args:
            symbol: Symbol name (e.g., "EURUSD")
            order_type: Order type ("BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT", "BUY_STOP", "SELL_STOP")
            volume: Order volume in lots
            price: Order price (required for limit/stop orders)
            sl: Stop loss price (optional)
            tp: Take profit price (optional)
            comment: Order comment
        
        Returns:
            Dictionary with order placement result or None if failed
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            # Map order type strings to mt5 constants
            order_type_map = {
                'BUY': mt5.ORDER_TYPE_BUY,
                'SELL': mt5.ORDER_TYPE_SELL,
                'BUY_LIMIT': mt5.ORDER_TYPE_BUY_LIMIT,
                'SELL_LIMIT': mt5.ORDER_TYPE_SELL_LIMIT,
                'BUY_STOP': mt5.ORDER_TYPE_BUY_STOP,
                'SELL_STOP': mt5.ORDER_TYPE_SELL_STOP,
            }
            
            if order_type not in order_type_map:
                raise ValueError(f"Invalid order type: {order_type}")
            
            # Get current symbol info for price
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                raise MT5OperationError(f"Symbol {symbol} not found")
            
            # Use current ask/bid if price not provided for market orders
            if price is None and order_type in ['BUY', 'SELL']:
                price = symbol_info.ask if order_type == 'BUY' else symbol_info.bid
            
            if price is None:
                raise ValueError("Price is required for limit/stop orders")
            
            # Create request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type_map[order_type],
                "price": price,
                "comment": comment,
            }
            
            # Add stop loss if provided
            if sl is not None:
                request["sl"] = sl
            
            # Add take profit if provided
            if tp is not None:
                request["tp"] = tp
            
            self.logger.info(f"Placing {order_type} order for {symbol}, volume: {volume}, price: {price}")
            
            # Send order
            result = mt5.order_send(request)
            
            if result is None:
                raise MT5OperationError(f"Order send failed for {symbol}")
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order rejected: {result.comment} (retcode: {result.retcode})"
                self.logger.error(error_msg)
                raise MT5OperationError(error_msg)
            
            result_dict = {
                'order_id': result.order,
                'retcode': result.retcode,
                'comment': result.comment,
                'symbol': symbol,
                'order_type': order_type,
                'volume': volume,
                'price': price,
                'sl': sl,
                'tp': tp,
            }
            
            self.logger.info(f"Order placed successfully. Order ID: {result.order}")
            return result_dict
            
        except MT5ConnectionError:
            raise
        except (ValueError, MT5OperationError) as e:
            self.logger.error(f"Order placement error: {str(e)}")
            raise MT5OperationError(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error placing order: {str(e)}")
            raise MT5OperationError(f"Failed to place order: {str(e)}")

    def close_position(
        self,
        ticket: int,
        symbol: Optional[str] = None,
        volume: Optional[float] = None,
        comment: str = "MT5Connector Close"
    ) -> Optional[Dict[str, Any]]:
        """
        Close an open position.
        
        Args:
            ticket: Position ticket/order ID
            symbol: Symbol name (optional, will be retrieved if not provided)
            volume: Volume to close (optional, closes entire position if not provided)
            comment: Close comment
        
        Returns:
            Dictionary with close result or None if failed
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            self.logger.info(f"Attempting to close position ticket: {ticket}")
            
            # Get position info if symbol not provided
            if symbol is None:
                position = mt5.positions_get(ticket=ticket)
                if not position:
                    raise MT5OperationError(f"Position with ticket {ticket} not found")
                symbol = position[0].symbol
                if volume is None:
                    volume = position[0].volume
            
            # Get current price
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                raise MT5OperationError(f"Symbol {symbol} not found")
            
            # Determine close type based on position type
            position = mt5.positions_get(ticket=ticket)
            if not position:
                raise MT5OperationError(f"Position with ticket {ticket} not found")
            
            position_type = position[0].type
            close_price = symbol_info.bid if position_type == mt5.POSITION_TYPE_BUY else symbol_info.ask
            
            # Create close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL if position_type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": ticket,
                "price": close_price,
                "comment": comment,
            }
            
            result = mt5.order_send(request)
            
            if result is None:
                raise MT5OperationError(f"Position close failed for ticket {ticket}")
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Position close rejected: {result.comment} (retcode: {result.retcode})"
                self.logger.error(error_msg)
                raise MT5OperationError(error_msg)
            
            result_dict = {
                'order_id': result.order,
                'ticket': ticket,
                'symbol': symbol,
                'volume': volume,
                'close_price': close_price,
                'retcode': result.retcode,
                'comment': result.comment,
            }
            
            self.logger.info(f"Position closed successfully. Ticket: {ticket}, Order ID: {result.order}")
            return result_dict
            
        except MT5ConnectionError:
            raise
        except MT5OperationError as e:
            self.logger.error(f"Close position error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error closing position: {str(e)}")
            raise MT5OperationError(f"Failed to close position: {str(e)}")

    def modify_order(
        self,
        ticket: int,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        price: Optional[float] = None,
        comment: str = "MT5Connector Modify"
    ) -> Optional[Dict[str, Any]]:
        """
        Modify an existing order or position.
        
        Args:
            ticket: Order/position ticket ID
            sl: New stop loss price (optional)
            tp: New take profit price (optional)
            price: New order price for pending orders (optional)
            comment: Modification comment
        
        Returns:
            Dictionary with modification result or None if failed
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            if sl is None and tp is None and price is None:
                raise ValueError("At least one parameter (sl, tp, or price) must be provided")
            
            self.logger.info(f"Attempting to modify order/position ticket: {ticket}")
            
            # Get order/position info
            orders = mt5.orders_get(ticket=ticket)
            positions = mt5.positions_get(ticket=ticket)
            
            if not orders and not positions:
                raise MT5OperationError(f"Order/position with ticket {ticket} not found")
            
            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_MODIFY,
                "position": ticket,
                "comment": comment,
            }
            
            # Add optional parameters
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp
            if price is not None:
                request["price"] = price
            
            result = mt5.order_send(request)
            
            if result is None:
                raise MT5OperationError(f"Order/position modification failed for ticket {ticket}")
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Modification rejected: {result.comment} (retcode: {result.retcode})"
                self.logger.error(error_msg)
                raise MT5OperationError(error_msg)
            
            result_dict = {
                'ticket': ticket,
                'sl': sl,
                'tp': tp,
                'price': price,
                'retcode': result.retcode,
                'comment': result.comment,
            }
            
            self.logger.info(f"Order/position modified successfully. Ticket: {ticket}")
            return result_dict
            
        except MT5ConnectionError:
            raise
        except (ValueError, MT5OperationError) as e:
            self.logger.error(f"Modify order error: {str(e)}")
            raise MT5OperationError(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error modifying order: {str(e)}")
            raise MT5OperationError(f"Failed to modify order: {str(e)}")

    def get_open_positions(self) -> Optional[pd.DataFrame]:
        """
        Retrieve all open positions.
        
        Returns:
            DataFrame with open positions or None if none exist
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            self.logger.info("Fetching open positions...")
            
            positions = mt5.positions_get()
            
            if not positions:
                self.logger.info("No open positions found")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(positions)
            
            # Select relevant columns
            columns_to_keep = [
                'ticket', 'symbol', 'type', 'volume', 'open_price',
                'sl', 'tp', 'open_time', 'comment', 'profit', 'time_update'
            ]
            
            # Only keep columns that exist
            columns_to_keep = [col for col in columns_to_keep if col in df.columns]
            df = df[columns_to_keep]
            
            # Convert time columns
            if 'open_time' in df.columns:
                df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
            if 'time_update' in df.columns:
                df['time_update'] = pd.to_datetime(df['time_update'], unit='s')
            
            # Convert position type to string
            if 'type' in df.columns:
                type_map = {0: 'BUY', 1: 'SELL'}
                df['type'] = df['type'].map(type_map)
            
            self.logger.info(f"Retrieved {len(df)} open positions")
            return df
            
        except MT5ConnectionError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving open positions: {str(e)}")
            raise MT5OperationError(f"Failed to get open positions: {str(e)}")

    def get_orders(self) -> Optional[pd.DataFrame]:
        """
        Retrieve all pending orders.
        
        Returns:
            DataFrame with pending orders or None if none exist
            
        Raises:
            MT5OperationError: If operation fails
        """
        try:
            if not self.is_connected:
                raise MT5ConnectionError("Not connected to MT5")
            
            self.logger.info("Fetching pending orders...")
            
            orders = mt5.orders_get()
            
            if not orders:
                self.logger.info("No pending orders found")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(orders)
            
            # Select relevant columns
            columns_to_keep = [
                'ticket', 'symbol', 'type', 'volume', 'price_open',
                'price_current', 'sl', 'tp', 'time_setup', 'time_setup_msc',
                'comment', 'reason', 'state'
            ]
            
            # Only keep columns that exist
            columns_to_keep = [col for col in columns_to_keep if col in df.columns]
            df = df[columns_to_keep]
            
            # Convert time columns
            if 'time_setup' in df.columns:
                df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
            
            self.logger.info(f"Retrieved {len(df)} pending orders")
            return df
            
        except MT5ConnectionError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving orders: {str(e)}")
            raise MT5OperationError(f"Failed to get orders: {str(e)}")

    def is_ready(self) -> bool:
        """
        Check if connector is ready for trading (connected and authenticated).
        
        Returns:
            True if connected and account info available, False otherwise
        """
        return self.is_connected and self.account_info is not None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures disconnection."""
        self.disconnect()
        return False
