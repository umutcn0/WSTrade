from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PriceData(BaseModel):
    timestamp: datetime
    symbol: str
    price: float
    quantity: float
    
class TradingSignal(BaseModel):
    timestamp: datetime
    symbol: str
    signal_type: str  # "BUY" or "SELL"
    price: float
    short_sma: float
    long_sma: float
    
class Order(BaseModel):
    order_id: str
    timestamp: datetime
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    price: float
    status: str
    filled_quantity: Optional[float] = None
    filled_price: Optional[float] = None
    
class Position(BaseModel):
    symbol: str
    side: str
    entry_price: float
    quantity: float
    timestamp: datetime
    pnl: Optional[float] = None
    status: str  # "OPEN" or "CLOSED" 