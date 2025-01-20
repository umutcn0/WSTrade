import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = "algotrading"
    
    # Redis
    REDIS_URI: str = os.getenv("REDIS_URI", "redis://localhost:6379")
    
    # Binance
    TRADING_PAIR: str = "BTCUSDT"
    KLINE_INTERVAL: str = "1s"  # 1 second interval for real-time data
    
    # Trading Parameters
    SHORT_TERM_PERIOD: int = 50
    LONG_TERM_PERIOD: int = 200
    
    class Config:
        case_sensitive = True

settings = Settings() 