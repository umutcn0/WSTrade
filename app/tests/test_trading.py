import pytest
from datetime import datetime, timezone, timedelta
from app.services.trading import TradingStrategy
from app.models.models import PriceData

@pytest.mark.asyncio
async def test_sma_calculation(test_db):
    strategy = TradingStrategy(database=test_db)
    
    # Generate test price data
    base_time = datetime.now(tz=timezone.utc)
    prices = []
    
    # Create ascending prices for a buy signal
    for i in range(strategy.long_period):
        price = 50000.0 + (i * 10)  # Increasing price trend
        price_data = PriceData(
            timestamp=base_time + timedelta(minutes=i),
            symbol="BTCUSDT",
            price=price,
            quantity=1.0
        )
        await test_db.save_price_data(price_data)
        prices.append(price_data)
    
    # Test SMA calculation
    short_sma, long_sma = await strategy.calculate_sma(prices)
    assert short_sma > long_sma  # Short-term SMA should be higher in uptrend

@pytest.mark.asyncio
async def test_buy_signal_generation(test_db):
    strategy = TradingStrategy(database=test_db)
    # Use shorter periods for testing
    strategy.short_period = 5
    strategy.long_period = 10
    base_time = datetime.now(tz=timezone.utc)

    for i in range(strategy.long_period - 5):
        price = 50000.0 - (i * 100)
        price_data = PriceData(
            timestamp=base_time + timedelta(minutes=i),
            symbol="BTCUSDT",
            price=price,
            quantity=1.0
        )
        await test_db.save_price_data(price_data)

    for i in range(5):
        price = 45000.0 + (i * 2000)
        price_data = PriceData(
            timestamp=base_time + timedelta(minutes=strategy.long_period - 3 + i),
            symbol="BTCUSDT",
            price=price,
            quantity=1.0
        )
        await test_db.save_price_data(price_data)

    # Test signal generation
    signal = await strategy.generate_signal("BTCUSDT", 50000.0)
    assert signal is not None
    assert signal.signal_type == "BUY"

@pytest.mark.asyncio
async def test_sell_signal_generation(test_db):
    strategy = TradingStrategy(database=test_db)
    # Use shorter periods for testing
    strategy.short_period = 5
    strategy.long_period = 10
    base_time = datetime.now(tz=timezone.utc)

    for i in range(strategy.long_period - 5):
        price = 50000.0 + (i * 100)
        price_data = PriceData(
            timestamp=base_time + timedelta(minutes=i),
            symbol="BTCUSDT",
            price=price,
            quantity=1.0
        )
        await test_db.save_price_data(price_data)

    for i in range(5):
        price = 55000.0 - (i * 2000)
        price_data = PriceData(
            timestamp=base_time + timedelta(minutes=strategy.long_period - 3 + i),
            symbol="BTCUSDT",
            price=price,
            quantity=1.0
        )
        await test_db.save_price_data(price_data)

    # Test signal generation
    signal = await strategy.generate_signal("BTCUSDT", 53000.0)
    assert signal is not None
    assert signal.signal_type == "SELL" 