import pytest
import json
from app.services.websocket import BinanceWebsocket, WebSocketClient

@pytest.mark.asyncio
async def test_websocket_message_handling(test_db):
    ws = BinanceWebsocket(database=test_db)
    
    # Create a properly formatted message
    message = {
        "e": "kline",
        "E": 1619999999999,
        "s": "BTCUSDT",
        "k": {
            "t": 1619999940000,
            "T": 1619999999999,
            "s": "BTCUSDT",
            "i": "1s",
            "f": 100,
            "L": 200,
            "o": "50000.00",
            "c": "51000.00",
            "h": "51100.00",
            "l": "49900.00",
            "v": "10.5",
            "n": 100,
            "x": False,
            "q": "525000.00",
            "V": "5.2",
            "Q": "260000.00",
            "B": "0"
        }
    }
    
    # Test message handling
    await ws.handle_message(message)
    
    # Verify price data was saved
    collection = test_db.client[test_db.settings.DB_NAME]["price_data"]
    saved_data = await collection.find_one({"symbol": "BTCUSDT"})
    assert saved_data is not None
    assert saved_data["price"] == 51000.00  # From mock data

@pytest.mark.asyncio
async def test_websocket_connection_error_handling(monkeypatch):
    ws = BinanceWebsocket()
    
    # Mock the websockets.connect to raise an exception
    async def mock_connect(*args, **kwargs):
        raise ConnectionError("Mock connection error")
    
    monkeypatch.setattr("websockets.connect", mock_connect)
    
    # Test that the connection error is handled gracefully
    with pytest.raises(ConnectionError) as exc_info:
        await ws.connect()
    assert "Mock connection error" in str(exc_info.value)
    assert not ws.is_healthy()

@pytest.mark.asyncio
async def test_websocket_reconnection_delay(monkeypatch):
    ws = BinanceWebsocket()
    
    # Test that reconnection delay increases exponentially
    assert ws.reconnect_delay == 1
    
    # Simulate a failed connection
    async def mock_connect(*args, **kwargs):
        raise ConnectionError("Mock connection error")
    
    monkeypatch.setattr("websockets.connect", mock_connect)
    
    # First attempt
    with pytest.raises(ConnectionError):
        await ws.connect()
    assert ws.reconnect_delay == 2
    
    # Second attempt
    with pytest.raises(ConnectionError):
        await ws.connect()
    assert ws.reconnect_delay == 4

@pytest.mark.asyncio
async def test_websocket_connection(mock_websocket):
    # Create client and connect
    client = WebSocketClient()
    client.ws = mock_websocket
    
    # Verify connection
    assert client.ws == mock_websocket

@pytest.mark.asyncio
async def test_websocket_receive_message(mock_websocket, mock_websocket_message):
    # Setup client with mock
    client = WebSocketClient()
    client.ws = mock_websocket
    mock_websocket.recv.return_value = json.dumps(mock_websocket_message)
    
    # Get message and verify
    message = await client.receive_message()
    assert message == mock_websocket_message
    mock_websocket.recv.assert_called_once()  # Verify recv was called exactly once 