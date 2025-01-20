import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import psutil

from app.services.database import db
from app.services.websocket import binance_ws
from app.api.endpoints import router

# Initialize Prometheus metrics
WEBSOCKET_MESSAGES = Counter('websocket_messages_total', 'Total WebSocket messages received')
TRADING_SIGNALS = Counter('trading_signals_total', 'Total trading signals generated')
LATENCY = Histogram('operation_latency_seconds', 'Time spent processing operations')
CPU_USAGE = Gauge('cpu_usage_percent', 'Current CPU usage percentage')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Current memory usage percentage')

async def collect_metrics():
    while True:
        CPU_USAGE.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().percent)
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_http_server(9090)
    await db.connect_to_database()
    print("Database connected")
    asyncio.create_task(binance_ws.start())
    print("Binance WebSocket connected")
    asyncio.create_task(collect_metrics())
    print("Metrics collector started")
    yield
    # Shutdown
    await db.close_database_connection()

app = FastAPI(title="Algotrading API", lifespan=lifespan)
app.include_router(router) 