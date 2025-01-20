import numpy as np
import pandas as pd
from datetime import datetime, timezone
from app.services.database import db
from app.models.models import TradingSignal, Order, Position, PriceData
from app.core.config import settings

class TradingStrategy:
    def __init__(self, database=None):
        self.short_period = settings.SHORT_TERM_PERIOD
        self.long_period = settings.LONG_TERM_PERIOD
        self.current_position = None
        self.db = database or db
        
    async def calculate_sma(self, prices):
        # Convert list of PriceData objects to DataFrame
        df = pd.DataFrame([{
            'price': p.price,
            'timestamp': p.timestamp
        } for p in prices])
        
        # If we don't have enough data points for the long SMA, use all available points
        short_window = min(self.short_period, len(df))
        long_window = min(self.long_period, len(df))
        
        short_sma = df['price'].rolling(window=short_window, min_periods=1).mean()
        long_sma = df['price'].rolling(window=long_window, min_periods=1).mean()
        
        
        return short_sma.iloc[-1], long_sma.iloc[-1]
        
    async def generate_signal(self, symbol: str, current_price: float):
        prices = await self.db.get_recent_prices(symbol, self.long_period)
        if len(prices) < self.long_period:
            return None
            
        short_sma, long_sma = await self.calculate_sma(prices)
        
        prev_prices = prices[:-1]  # Excluding the current price
        prev_short_sma, prev_long_sma = await self.calculate_sma(prev_prices)

        signal = None
        if prev_short_sma < prev_long_sma and short_sma > long_sma:
            signal = "BUY"
        elif prev_short_sma > prev_long_sma and short_sma < long_sma:
            signal = "SELL"
            
        if signal:
            trading_signal = TradingSignal(
                timestamp=datetime.now(tz=timezone.utc),
                symbol=symbol,
                signal_type=signal,
                price=current_price,
                short_sma=short_sma,
                long_sma=long_sma
            )
            print(f"Trading signal saved for {symbol} at {current_price}")
            await self.db.save_trading_signal(trading_signal)
            return trading_signal
        return None
        
    async def execute_signal(self, signal: TradingSignal):
        order = Order(
            order_id=f"mock_{datetime.now(tz=timezone.utc).timestamp()}",
            timestamp=datetime.now(tz=timezone.utc),
            symbol=signal.symbol,
            side=signal.signal_type,
            quantity=1.0,
            price=signal.price,
            status="FILLED"
        )
        await self.db.save_order(order)
        
        if signal.signal_type == "BUY":
            position = Position(
                symbol=signal.symbol,
                side="LONG",
                entry_price=signal.price,
                quantity=1.0,
                timestamp=datetime.now(tz=timezone.utc),
                status="OPEN"
            )
            await self.db.save_position(position)
            self.current_position = position
        elif signal.signal_type == "SELL" and self.current_position:
            pnl = (signal.price - self.current_position.entry_price) * self.current_position.quantity
            await self.db.update_position(
                signal.symbol,
                {
                    "status": "CLOSED",
                    "pnl": pnl
                }
            )
            self.current_position = None

class TradingService:
    def __init__(self, db, websocket):
        self.db = db
        self.websocket = websocket
        self.strategy = TradingStrategy()
        
    async def process_market_data(self):
        message = await self.websocket.receive_message()
        if message:
            price_data = PriceData(
                timestamp=datetime.now(tz=timezone.utc),
                symbol=settings.TRADING_PAIR,
                price=float(message['k']['c']),
                quantity=float(message['k']['v'])
            )
            await self.db.save_price_data(price_data)
            signal = await self.strategy.generate_signal(settings.TRADING_PAIR, price_data.price)
            if signal:
                await self.strategy.execute_signal(signal)

strategy = TradingStrategy() 