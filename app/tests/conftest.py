import pytest
import pytest_asyncio
import asyncio
from app.core.config import settings
from app.services.database import Database
import unittest.mock

@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_db():
    # Use a test database
    test_settings = settings.model_copy()
    test_settings.DB_NAME = "test_algotrading"
    test_settings.MONGODB_URI = "mongodb://localhost:27017"
    
    db = Database()
    db.settings = test_settings
    await db.connect_to_database()
    
    # Create indexes
    await db.client[test_settings.DB_NAME]["price_data"].create_index("symbol")
    await db.client[test_settings.DB_NAME]["trading_signals"].create_index("symbol")
    await db.client[test_settings.DB_NAME]["orders"].create_index("order_id")
    await db.client[test_settings.DB_NAME]["positions"].create_index([("symbol", 1), ("status", 1)])
    
    yield db
    
    # Cleanup: Drop test database
    if db.client:
        await db.client.drop_database(test_settings.DB_NAME)
        await db.close_database_connection()

@pytest.fixture
def mock_websocket_message():
    return {
        "e": "kline",
        "E": 1619999999999,
        "s": "BTCUSDT",
        "k": {
            "t": 1619999940000,  # Kline start time
            "T": 1619999999999,  # Kline close time
            "s": "BTCUSDT",      # Symbol
            "i": "1s",           # Interval
            "f": 100,            # First trade ID
            "L": 200,            # Last trade ID
            "o": "50000.00",     # Open price
            "c": "51000.00",     # Close price
            "h": "51100.00",     # High price
            "l": "49900.00",     # Low price
            "v": "10.5",         # Base asset volume
            "n": 100,            # Number of trades
            "x": False,          # Is this kline closed?
            "q": "525000.00",    # Quote asset volume
            "V": "5.2",          # Taker buy base asset volume
            "Q": "260000.00",    # Taker buy quote asset volume
            "B": "0"             # Ignore
        }
    }

@pytest.fixture
def mock_websocket():
    class MockWebSocket:
        def __init__(self):
            self.recv = unittest.mock.AsyncMock()
            self.send = unittest.mock.AsyncMock()
            self.close = unittest.mock.AsyncMock()
    return MockWebSocket()