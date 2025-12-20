"""
Instrument Token Utility for Zerodha.

Helps manage instrument tokens and symbol lookups for WebSocket streaming.
"""

from typing import Dict, List, Optional
import pandas as pd
from loguru import logger


class InstrumentManager:
    """
    Manages Zerodha instrument tokens and symbol mappings.
    
    Example:
        >>> manager = InstrumentManager(broker)
        >>> manager.load_instruments()
        >>> token = manager.get_token("NSE:INFY")
        >>> symbol = manager.get_symbol(408065)
    """
    
    def __init__(self, broker=None):
        """
        Initialize instrument manager.
        
        Args:
            broker: Optional ZerodhaBroker instance
        """
        self.broker = broker
        self._instruments: pd.DataFrame = pd.DataFrame()
        self._symbol_to_token: Dict[str, int] = {}
        self._token_to_symbol: Dict[int, str] = {}
    
    def load_instruments(self, exchange: Optional[str] = None) -> None:
        """
        Load instruments from broker.
        
        Args:
            exchange: Optional exchange filter (NSE, BSE, NFO, etc.)
        """
        if not self.broker:
            raise ValueError("Broker required to load instruments")
        
        logger.info(f"Loading instruments{f' for {exchange}' if exchange else ''}...")
        
        try:
            # Get instruments from Kite API
            kite = self.broker._get_kite()
            instruments = kite.instruments(exchange=exchange)
            
            # Convert to DataFrame
            self._instruments = pd.DataFrame(instruments)
            
            # Build lookups
            self._build_lookups()
            
            logger.info(f"✅ Loaded {len(self._instruments)} instruments")
            
        except Exception as e:
            logger.error(f"Failed to load instruments: {e}")
            raise
    
    def _build_lookups(self) -> None:
        """Build symbol/token lookup dictionaries."""
        self._symbol_to_token.clear()
        self._token_to_symbol.clear()
        
        for _, row in self._instruments.iterrows():
            token = row['instrument_token']
            exchange = row['exchange']
            symbol = row['tradingsymbol']
            
            # Format: EXCHANGE:SYMBOL
            full_symbol = f"{exchange}:{symbol}"
            
            self._symbol_to_token[full_symbol] = token
            self._token_to_symbol[token] = full_symbol
    
    def get_token(self, symbol: str) -> Optional[int]:
        """
        Get instrument token for symbol.
        
        Args:
            symbol: Symbol in EXCHANGE:SYMBOL format
            
        Returns:
            Instrument token or None
        """
        return self._symbol_to_token.get(symbol)
    
    def get_symbol(self, token: int) -> Optional[str]:
        """
        Get symbol for instrument token.
        
        Args:
            token: Instrument token
            
        Returns:
            Symbol or None
        """
        return self._token_to_symbol.get(token)
    
    def get_tokens(self, symbols: List[str]) -> List[int]:
        """
        Get tokens for multiple symbols.
        
        Args:
            symbols: List of symbols
            
        Returns:
            List of tokens (None for not found)
        """
        tokens = []
        for symbol in symbols:
            token = self.get_token(symbol)
            if token:
                tokens.append(token)
            else:
                logger.warning(f"Token not found for {symbol}")
        
        return tokens
    
    def search(self, query: str, exchange: Optional[str] = None) -> pd.DataFrame:
        """
        Search instruments by name.
        
        Args:
            query: Search query (partial symbol name)
            exchange: Optional exchange filter
            
        Returns:
            DataFrame of matching instruments
        """
        df = self._instruments
        
        if exchange:
            df = df[df['exchange'] == exchange]
        
        # Search in tradingsymbol and name
        mask = (
            df['tradingsymbol'].str.contains(query, case=False, na=False) |
            df['name'].str.contains(query, case=False, na=False)
        )
        
        return df[mask][['instrument_token', 'exchange', 'tradingsymbol', 'name', 'instrument_type']]
    
    def get_popular_stocks(self, exchange: str = "NSE", limit: int = 20) -> Dict[str, int]:
        """
        Get popular stock symbols with their tokens.
        
        Args:
            exchange: Exchange (default: NSE)
            limit: Number of stocks
            
        Returns:
            Dict mapping symbols to tokens
        """
        # Popular NSE stocks
        popular_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
            "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
            "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA",
            "TITAN", "WIPRO", "ULTRACEMCO", "NESTLEIND", "HCLTECH"
        ]
        
        result = {}
        for symbol in popular_symbols[:limit]:
            full_symbol = f"{exchange}:{symbol}"
            token = self.get_token(full_symbol)
            if token:
                result[full_symbol] = token
        
        return result
    
    def export_lookup(self, filename: str = "instrument_lookup.json") -> None:
        """Export symbol/token lookup to JSON file."""
        import json
        
        with open(filename, "w") as f:
            json.dump(self._symbol_to_token, f, indent=2)
        
        logger.info(f"Exported {len(self._symbol_to_token)} instruments to {filename}")
    
    def import_lookup(self, filename: str = "instrument_lookup.json") -> None:
        """Import symbol/token lookup from JSON file."""
        import json
        
        with open(filename, "r") as f:
            self._symbol_to_token = json.load(f)
        
        # Build reverse lookup
        self._token_to_symbol = {v: k for k, v in self._symbol_to_token.items()}
        
        logger.info(f"Imported {len(self._symbol_to_token)} instruments from {filename}")
    
    def get_statistics(self) -> Dict:
        """Get statistics."""
        exchanges = {}
        if not self._instruments.empty:
            exchanges = self._instruments['exchange'].value_counts().to_dict()
        
        return {
            'total_instruments': len(self._instruments),
            'exchanges': exchanges,
            'lookups_loaded': len(self._symbol_to_token)
        }
