from fastapi import APIRouter, HTTPException
import psutil
from app.services.database import db
from app.services.websocket import binance_ws
from app.core.config import settings
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/health")
async def health_check():
    if not binance_ws.is_healthy():
        raise HTTPException(status_code=503, detail="WebSocket connection is down")
    return {"status": "healthy"}

@router.get("/metrics/trading")
async def trading_metrics():
    collection = db.client[settings.DB_NAME]["trading_signals"]
    total_signals = await collection.count_documents({})
    
    collection = db.client[settings.DB_NAME]["positions"]
    total_positions = await collection.count_documents({})
    closed_positions = await collection.count_documents({"status": "CLOSED"})
    
    cursor = collection.find({"status": "CLOSED"})
    total_pnl = sum([position.get("pnl", 0) async for position in cursor])
    
    return {
        "total_signals": total_signals,
        "total_positions": total_positions,
        "closed_positions": closed_positions,
        "total_pnl": total_pnl
    }

@router.get("/metrics/system", response_class=PlainTextResponse)
async def system_metrics():
    metrics = []
    
    # CPU usage metric
    cpu = psutil.cpu_percent()
    metrics.append(f"# HELP cpu_usage_percent Current CPU usage percentage")
    metrics.append(f"# TYPE cpu_usage_percent gauge")
    metrics.append(f"cpu_usage_percent {cpu}")
    
    # Memory usage metric
    memory = psutil.virtual_memory().percent
    metrics.append(f"# HELP memory_usage_percent Current memory usage percentage")
    metrics.append(f"# TYPE memory_usage_percent gauge")
    metrics.append(f"memory_usage_percent {memory}")
    
    # Disk usage metric
    disk = psutil.disk_usage('/').percent
    metrics.append(f"# HELP disk_usage_percent Current disk usage percentage")
    metrics.append(f"# TYPE disk_usage_percent gauge")
    metrics.append(f"disk_usage_percent {disk}")
    
    return "\n".join(metrics) 