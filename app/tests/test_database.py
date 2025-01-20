import pytest
from datetime import datetime, timezone, timedelta
from app.models.models import PriceData, TradingSignal, Order

pytestmark = pytest.mark.asyncio

async def test_database_connection(test_db):
    assert test_db.client is not None
    assert await test_db.client.server_info() is not None

async def test_database_operations(test_db):
    collection = test_db.client[test_db.settings.DB_NAME]["test_collection"]
    await collection.insert_one({"test": "data"})
    result = await collection.find_one({"test": "data"})
    assert result["test"] == "data"

@pytest.mark.asyncio
async def test_save_price_data(test_db):
    price_data = PriceData(
        timestamp=datetime.now(tz=timezone.utc),
        symbol="BTCUSDT",
        price=50000.0,
        quantity=1.0
    )
    
    await test_db.save_price_data(price_data)
    
    # Verify data was saved
    collection = test_db.client[test_db.settings.DB_NAME]["price_data"]
    saved_data = await collection.find_one({"symbol": "BTCUSDT"})
    assert saved_data is not None
    assert saved_data["price"] == 50000.0

@pytest.mark.asyncio
async def test_save_trading_signal(test_db):
    signal = TradingSignal(
        timestamp=datetime.now(tz=timezone.utc),
        symbol="BTCUSDT",
        signal_type="BUY",
        price=50000.0,
        short_sma=49000.0,
        long_sma=48000.0
    )
    
    await test_db.save_trading_signal(signal)
    
    collection = test_db.client[test_db.settings.DB_NAME]["trading_signals"]
    saved_signal = await collection.find_one({"symbol": "BTCUSDT"})
    assert saved_signal is not None
    assert saved_signal["signal_type"] == "BUY"

@pytest.mark.asyncio
async def test_save_and_update_order(test_db):
    order = Order(
        order_id="test_order_1",
        timestamp=datetime.now(tz=timezone.utc),
        symbol="BTCUSDT",
        side="BUY",
        quantity=1.0,
        price=50000.0,
        status="NEW"
    )
    
    await test_db.save_order(order)
    
    # Update order
    update_data = {"status": "FILLED", "filled_price": 50100.0}
    await test_db.update_order(order.order_id, update_data)
    
    collection = test_db.client[test_db.settings.DB_NAME]["orders"]
    updated_order = await collection.find_one({"order_id": "test_order_1"})
    assert updated_order is not None
    assert updated_order["status"] == "FILLED"
    assert updated_order["filled_price"] == 50100.0

@pytest.mark.asyncio
async def test_get_recent_prices(test_db):
    base_time = datetime.now(tz=timezone.utc)
    # Insert multiple price points with different timestamps
    prices = [
        PriceData(
            timestamp=base_time + timedelta(seconds=i),
            symbol="BTCUSDT",
            price=float(50000 + i),
            quantity=1.0
        ) for i in range(5)
    ]
    
    for price in prices:
        await test_db.save_price_data(price)
    
    # Test retrieval
    recent_prices = await test_db.get_recent_prices("BTCUSDT", limit=3)
    assert len(recent_prices) == 3
    # Most recent prices should be first (highest timestamp)
    assert recent_prices[0].price == 50004.0  # Last price inserted
    assert recent_prices[1].price == 50003.0
    assert recent_prices[2].price == 50002.0 