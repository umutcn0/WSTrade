from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import PriceData, TradingSignal, Order, Position

class Database:
    client: AsyncIOMotorClient = None
    settings = settings
    
    async def connect_to_database(self):
        print(f"Connecting to MongoDB at {settings.MONGODB_URI}")
        self.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test the connection
        try:
            await self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            raise
        
    async def close_database_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
            
    async def save_price_data(self, price_data: PriceData):
        collection = self.client[self.settings.DB_NAME]["price_data"]
        data = price_data.model_dump()
        result = await collection.insert_one(data)
        
    async def save_trading_signal(self, signal: TradingSignal):
        collection = self.client[self.settings.DB_NAME]["trading_signals"]
        data = signal.model_dump()
        result = await collection.insert_one(data)
        
    async def save_order(self, order: Order):
        collection = self.client[self.settings.DB_NAME]["orders"]
        data = order.model_dump()
        await collection.insert_one(data)
        
    async def update_order(self, order_id: str, update_data: dict):
        collection = self.client[self.settings.DB_NAME]["orders"]
        await collection.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        
    async def save_position(self, position: Position):
        collection = self.client[self.settings.DB_NAME]["positions"]
        data = position.model_dump()
        await collection.insert_one(data)
        
    async def update_position(self, symbol: str, update_data: dict):
        collection = self.client[self.settings.DB_NAME]["positions"]
        await collection.update_one(
            {"symbol": symbol, "status": "OPEN"},
            {"$set": update_data}
        )
        
    async def get_recent_prices(self, symbol: str, limit: int = 200):
        collection = self.client[self.settings.DB_NAME]["price_data"]
        cursor = collection.find({"symbol": symbol}).sort("timestamp", -1).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [PriceData(**doc) for doc in documents]

db = Database() 