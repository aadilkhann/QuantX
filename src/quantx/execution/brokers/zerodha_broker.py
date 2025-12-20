"""
Zerodha Broker Implementation.

Integrates with Zerodha Kite Connect API for trading on Indian markets (NSE, BSE, MCX).
Supports equity, F&O, and currency trading.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from loguru import logger

from quantx.execution.brokers.base import (
    IBroker,
    BrokerFactory,
    Order,
    Fill,
    Position,
    Account,
    OrderType,
    OrderSide,
    OrderStatus,
    BrokerConnection
)


class ZerodhaBroker(IBroker):
    """
    Zerodha broker implementation using Kite Connect API.
    
    Supports trading on NSE, BSE, NFO, MCX, and other Indian exchanges.
    
    Features:
    - OAuth 2.0 authentication
    - Order placement (Market, Limit, SL, SL-M)
    - Position and holdings retrieval
    - Market data (quotes, OHLC)
    - Real-time updates via WebSocket
    
    Example:
        >>> broker = ZerodhaBroker("zerodha", {
        ...     "api_key": "your_api_key",
        ...     "api_secret": "your_api_secret",
        ...     "access_token": "your_access_token"  # Optional, will prompt if missing
        ... })
        >>> broker.connect()
        >>> order = Order("", "NSE:INFY", OrderSide.BUY, OrderType.MARKET, 1)
        >>> order_id = broker.place_order(order)
    
    Note:
        Requires kiteconnect package: pip install kiteconnect
    """
    
    # Order type mapping: QuantX -> Kite
    ORDER_TYPE_MAP = {
        OrderType.MARKET: "MARKET",
        OrderType.LIMIT: "LIMIT",
        OrderType.STOP: "SL",
        OrderType.STOP_LIMIT: "SL-M"
    }
    
    # Transaction type mapping
    TRANSACTION_TYPE_MAP = {
        OrderSide.BUY: "BUY",
        OrderSide.SELL: "SELL"
    }
    
    # Order status mapping: Kite -> QuantX
    STATUS_MAP = {
        "PENDING": OrderStatus.PENDING,
        "OPEN": OrderStatus.SUBMITTED,
        "COMPLETE": OrderStatus.FILLED,
        "CANCELLED": OrderStatus.CANCELLED,
        "REJECTED": OrderStatus.REJECTED,
        "MODIFIED": OrderStatus.SUBMITTED
    }
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize Zerodha broker.
        
        Args:
            name: Broker name
            config: Configuration dictionary with:
                - api_key: Kite Connect API key
                - api_secret: Kite Connect API secret
                - access_token: (Optional) Access token from OAuth flow
                - user_id: (Optional) Zerodha user ID
                - password: (Optional) For automated login
                - totp_key: (Optional) For 2FA
        """
        super().__init__(name, config)
        
        # Validate required config
        if "api_key" not in config:
            raise ValueError("api_key is required in config")
        if "api_secret" not in config:
            raise ValueError("api_secret is required in config")
        
        self.api_key = config["api_key"]
        self.api_secret = config["api_secret"]
        self.access_token = config.get("access_token")
        self.user_id = config.get("user_id")
        
        # Kite Connect instance (lazy loaded)
        self._kite = None
        
        # Session info
        self._session_data: Optional[Dict] = None
        
        # Rate limiting
        self._last_request_time = 0.0
        self._min_request_interval = 0.1  # 100ms between requests (10 req/sec)
        
        logger.info(f"ZerodhaBroker initialized with API key: {self.api_key[:10]}...")
    
    def _get_kite(self):
        """Get or create KiteConnect instance."""
        if self._kite is None:
            try:
                from kiteconnect import KiteConnect
                self._kite = KiteConnect(api_key=self.api_key)
                
                if self.access_token:
                    self._kite.set_access_token(self.access_token)
                    logger.info("Access token set from config")
                
            except ImportError:
                raise ImportError(
                    "kiteconnect package not installed. "
                    "Install with: pip install kiteconnect"
                )
        
        return self._kite
    
    def _rate_limit(self):
        """Implement rate limiting for API calls."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def connect(self) -> bool:
        """
        Connect to Zerodha.
        
        Returns:
            True if connection successful
        """
        try:
            kite = self._get_kite()
            
            # If no access token, need to do OAuth flow
            if not self.access_token:
                logger.warning(
                    "No access token found. Please complete OAuth flow manually.\n"
                    "1. Get login URL with get_login_url()\n"
                    "2. Login via browser\n"
                    "3. Call generate_session(request_token)"
                )
                self.connection.connected = False
                return False
            
            # Verify token by trying to get profile
            self._rate_limit()
            profile = kite.profile()
            
            self.connection.connected = True
            self.connection.authenticated = True
            self.connection.last_heartbeat = datetime.now()
            
            logger.info(f"✅ Connected to Zerodha as {profile.get('user_name', 'Unknown')}")
            logger.info(f"   User ID: {profile.get('user_id')}")
            logger.info(f"   Email: {profile.get('email')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Zerodha: {e}")
            self.connection.connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from Zerodha.
        
        Returns:
            True if disconnection successful
        """
        try:
            # Kite Connect doesn't have explicit disconnect
            # Just invalidate the session
            self._kite = None
            self.access_token = None
            self.connection.connected = False
            self.connection.authenticated = False
            
            logger.info("Disconnected from Zerodha")
            return True
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to broker."""
        return self.connection.connected and self.connection.authenticated
    
    def get_login_url(self) -> str:
        """
        Get OAuth login URL.
        
        Returns:
            Login URL for browser authentication
        """
        kite = self._get_kite()
        login_url = kite.login_url()
        
        logger.info(f"Login URL: {login_url}")
        return login_url
    
    def generate_session(self, request_token: str) -> Dict[str, Any]:
        """
        Generate session using request token from OAuth callback.
        
        Args:
            request_token: Request token from OAuth callback
            
        Returns:
            Session data with access_token and other info
        """
        try:
            kite = self._get_kite()
            
            # Generate session
            session_data = kite.generate_session(
                request_token=request_token,
                api_secret=self.api_secret
            )
            
            self._session_data = session_data
            self.access_token = session_data["access_token"]
            self.user_id = session_data["user_id"]
            
            # Set access token for future requests
            kite.set_access_token(self.access_token)
            
            logger.info(f"✅ Session generated successfully")
            logger.info(f"   User ID: {session_data.get('user_id')}")
            logger.info(f"   Access Token: {self.access_token[:20]}...")
            
            # Save to config for future use
            self.config["access_token"] = self.access_token
            self.config["user_id"] = self.user_id
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to generate session: {e}")
            raise
    
    def place_order(self, order: Order) -> str:
        """
        Place an order.
        
        Args:
            order: Order to place
            
        Returns:
            Order ID from Zerodha
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Zerodha")
        
        if not self.validate_order(order):
            raise ValueError("Order validation failed")
        
        try:
            kite = self._get_kite()
            
            # Parse symbol (format: EXCHANGE:SYMBOL)
            if ":" in order.symbol:
                exchange, trading_symbol = order.symbol.split(":", 1)
            else:
                # Default to NSE if no exchange specified
                exchange = "NSE"
                trading_symbol = order.symbol
            
            # Prepare order params
            params = {
                "exchange": exchange,
                "tradingsymbol": trading_symbol,
                "transaction_type": self.TRANSACTION_TYPE_MAP[order.side],
                "quantity": int(order.quantity),
                "order_type": self.ORDER_TYPE_MAP[order.order_type],
                "product": "MIS",  # Intraday by default, can be configured
                "validity": "DAY"
            }
            
            # Add price for limit orders
            if order.order_type == OrderType.LIMIT:
                params["price"] = order.price
            
            # Add trigger price for stop orders
            if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
                params["trigger_price"] = order.stop_price
                if order.order_type == OrderType.STOP_LIMIT:
                    params["price"] = order.price
            
            # Place order with rate limiting
            self._rate_limit()
            response = kite.place_order(variety="regular", **params)
            
            order_id = str(response["order_id"])
            order.order_id = order_id
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = datetime.now()
            
            logger.info(
                f"✅ Order placed: {order_id} | {order.side.value} {order.quantity} "
                f"{order.symbol} @ {order.order_type.value}"
            )
            
            return order_id
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            order.status = OrderStatus.REJECTED
            raise
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancellation successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Zerodha")
        
        try:
            kite = self._get_kite()
            
            self._rate_limit()
            kite.cancel_order(variety="regular", order_id=order_id)
            
            logger.info(f"✅ Order cancelled: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get order details.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order object or None if not found
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Zerodha")
        
        try:
            kite = self._get_kite()
            
            self._rate_limit()
            orders = kite.orders()
            
            # Find order by ID
            for kite_order in orders:
                if str(kite_order["order_id"]) == str(order_id):
                    return self._convert_kite_order(kite_order)
            
            logger.warning(f"Order not found: {order_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            return None
    
    def get_open_orders(self) -> List[Order]:
        """
        Get all open orders.
        
        Returns:
            List of open orders
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Zerodha")
        
        try:
            kite = self._get_kite()
            
            self._rate_limit()
            kite_orders = kite.orders()
            
            # Filter open orders
            open_orders = []
            for kite_order in kite_orders:
                if kite_order["status"] in ["PENDING", "OPEN", "TRIGGER PENDING"]:
                    order = self._convert_kite_order(kite_order)
                    open_orders.append(order)
            
            logger.debug(f"Found {len(open_orders)} open orders")
            return open_orders
            
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []
    
    def get_positions(self) -> List[Position]:
        """
        Get all current positions.
        
        Returns:
            List of positions
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Zerodha")
        
        try:
            kite = self._get_kite()
            
            self._rate_limit()
            positions_data = kite.positions()
            
            # Get day positions (current day)
            day_positions = positions_data.get("day", [])
            
            positions = []
            for pos_data in day_positions:
                if pos_data["quantity"] != 0:  # Only non-zero positions
                    position = self._convert_kite_position(pos_data)
                    positions.append(position)
            
            logger.debug(f"Found {len(positions)} positions")
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a specific symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position object or None
        """
        positions = self.get_positions()
        
        for position in positions:
            if position.symbol == symbol or position.symbol.endswith(f":{symbol}"):
                return position
        
        return None
    
    def get_account(self) -> Account:
        """
        Get account information.
        
        Returns:
            Account object with balance and margin info
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Zerodha")
        
        try:
            kite = self._get_kite()
            
            self._rate_limit()
            margins = kite.margins()
            
            # Get equity margins
            equity_margin = margins.get("equity", {})
            
            # Get positions for unrealized P&L
            positions = self.get_positions()
            unrealized_pnl = sum(p.unrealized_pnl for p in positions)
            
            # Calculate equity
            available_cash = equity_margin.get("available", {}).get("live_balance", 0)
            used_margin = equity_margin.get("utilisedigin", 0)
            
            total_cash = available_cash + used_margin
            positions_value = sum(p.market_value for p in positions)
            equity = total_cash + positions_value
            
            account = Account(
                account_id=self.user_id or "zerodha",
                cash=available_cash,
                equity=equity,
                buying_power=equity_margin.get("available", {}).get("cash", 0),
                positions_value=positions_value,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=0.0,  # Not directly available from Kite
                initial_capital=total_cash  # Approximate
            )
            
            logger.debug(f"Account equity: ₹{equity:,.2f}")
            return account
            
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            raise
    
    def get_quote(self, symbol: str) -> Dict[str, float]:
        """
        Get current quote for a symbol.
        
        Args:
            symbol: Trading symbol (format: EXCHANGE:SYMBOL or just SYMBOL)
            
        Returns:
            Dictionary with bid, ask, last price
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Zerodha")
        
        try:
            kite = self._get_kite()
            
            # Format symbol for Kite
            if ":" not in symbol:
                symbol = f"NSE:{symbol}"
            
            self._rate_limit()
            quotes = kite.quote([symbol])
            
            if symbol in quotes:
                quote_data = quotes[symbol]
                return {
                    "bid": quote_data.get("depth", {}).get("buy", [{}])[0].get("price", 0.0),
                    "ask": quote_data.get("depth", {}).get("sell", [{}])[0].get("price", 0.0),
                    "last": quote_data.get("last_price", 0.0),
                    "volume": quote_data.get("volume", 0),
                    "open": quote_data.get("ohlc", {}).get("open", 0.0),
                    "high": quote_data.get("ohlc", {}).get("high", 0.0),
                    "low": quote_data.get("ohlc", {}).get("low", 0.0),
                    "close": quote_data.get("ohlc", {}).get("close", 0.0)
                }
            else:
                logger.warning(f"No quote data for {symbol}")
                return {"bid": 0.0, "ask": 0.0, "last": 0.0}
                
        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            return {"bid": 0.0, "ask": 0.0, "last": 0.0}
    
    def _convert_kite_order(self, kite_order: Dict) -> Order:
        """Convert Kite order to QuantX Order."""
        # Map order type
        order_type = OrderType.MARKET
        if kite_order["order_type"] == "LIMIT":
            order_type = OrderType.LIMIT
        elif kite_order["order_type"] in ["SL", "SL-M"]:
            order_type = OrderType.STOP
        
        # Map side
        side = OrderSide.BUY if kite_order["transaction_type"] == "BUY" else OrderSide.SELL
        
        # Map status
        status = self.STATUS_MAP.get(kite_order["status"], OrderStatus.PENDING)
        
        # Create symbol in EXCHANGE:SYMBOL format
        symbol = f"{kite_order['exchange']}:{kite_order['tradingsymbol']}"
        
        return Order(
            order_id=str(kite_order["order_id"]),
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=kite_order["quantity"],
            price=kite_order.get("price"),
            stop_price=kite_order.get("trigger_price"),
            status=status,
            filled_quantity=kite_order.get("filled_quantity", 0),
            average_fill_price=kite_order.get("average_price", 0.0),
            submitted_at=kite_order.get("order_timestamp"),
            metadata={"kite_order": kite_order}
        )
    
    def _convert_kite_position(self, pos_data: Dict) -> Position:
        """Convert Kite position to QuantX Position."""
        symbol = f"{pos_data['exchange']}:{pos_data['tradingsymbol']}"
        quantity = pos_data["quantity"]
        average_price = pos_data["average_price"]
        last_price = pos_data["last_price"]
        
        market_value = quantity * last_price
        unrealized_pnl = (last_price - average_price) * quantity
        
        return Position(
            symbol=symbol,
            quantity=quantity,
            average_price=average_price,
            current_price=last_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=pos_data.get("realised", 0.0)
        )


# Register Zerodha broker
BrokerFactory.register("zerodha", ZerodhaBroker)
