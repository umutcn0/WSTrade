import json
import asyncio
import websockets
from datetime import datetime, timezone
from app.models.models import PriceData
from app.services.database import db
from app.services.trading import strategy
from app.core.config import settings
import ssl

class WebSocketClient:
    def __init__(self):
        self.ws = None
        self.ws_url = f"wss://stream.binance.com:9443/ws/{settings.TRADING_PAIR.lower()}@kline_{settings.KLINE_INTERVAL}"
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        
    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, ssl=self.ssl_context)
        
    async def receive_message(self):
        if self.ws:
            message = await self.ws.recv()
            return json.loads(message)
        return None
        
    async def disconnect(self):
        if self.ws:
            await self.ws.close()

class BinanceWebsocket:
    def __init__(self, database=None):
        self.ws_url = f"wss://stream.binance.com:9443/ws/{settings.TRADING_PAIR.lower()}@kline_{settings.KLINE_INTERVAL}"
        self.is_connected = False
        self.reconnect_delay = 1
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.db = database or db  # Use provided database or global instance
        
    async def handle_message(self, message):
        try:
            data = json.loads(message) if isinstance(message, str) else message
            
            if 'k' not in data:
                print(f"Invalid message format: {data}")
                return
                
            kline = data['k']
            if 'c' not in kline or 'v' not in kline:
                print(f"Invalid kline format: {kline}")
                return
                
            price_data = PriceData(
                timestamp=datetime.now(tz=timezone.utc),
                symbol=settings.TRADING_PAIR,
                price=float(kline['c']),  # Closing price
                quantity=float(kline['v'])  # Volume
            )
            
            await self.db.save_price_data(price_data)
            
            signal = await strategy.generate_signal(settings.TRADING_PAIR, price_data.price)
            if signal:
                await strategy.execute_signal(signal)
        except Exception as e:
            print(f"Error handling message: {str(e)}")
            
    async def connect(self):
        try:
            websocket = await websockets.connect(self.ws_url, ssl=self.ssl_context)
            self.is_connected = True
            self.reconnect_delay = 1
            
            while True:
                try:
                    message = await websocket.recv()
                    await self.handle_message(message)
                except websockets.ConnectionClosed:
                    print("WebSocket connection closed")
                    break
                    
        except Exception as e:
            print(f"WebSocket error: {str(e)}")
            self.is_connected = False
            
            # Exponential backoff for reconnection
            self.reconnect_delay = min(self.reconnect_delay * 2, 60)
            print(f"Reconnecting in {self.reconnect_delay} seconds...")
            raise
                
    async def start(self):
        while True:
            try:
                await self.connect()
            except Exception as e:
                await asyncio.sleep(self.reconnect_delay)
                continue
        
    def is_healthy(self):
        return self.is_connected

binance_ws = BinanceWebsocket() 