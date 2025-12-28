"""
QuantX FastAPI Backend.

Modern REST API for web dashboard with WebSocket support.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from quantx.core import __version__
from quantx.monitoring import HealthMonitor
from quantx.api.routers import engine, positions, orders, pnl

# Create FastAPI app
app = FastAPI(
    title="QuantX API",
    description="REST API for QuantX Trading Platform",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(engine.router)
app.include_router(positions.router)
app.include_router(orders.router)
app.include_router(pnl.router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use dependency injection)
health_monitor = HealthMonitor()
active_websockets: List[WebSocket] = []


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "QuantX API",
        "version": __version__,
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns overall system health status.
    """
    health_dict = health_monitor.get_health_dict()
    
    # Return 200 if healthy, 503 if unhealthy
    status_code = 200 if health_dict["status"] == "healthy" else 503
    
    return JSONResponse(
        content=health_dict,
        status_code=status_code
    )


@app.get("/api/v1/info")
async def get_info():
    """Get system information."""
    return {
        "version": __version__,
        "name": "QuantX",
        "description": "AI-Powered Algorithmic Trading Platform",
        "features": {
            "backtesting": True,
            "ml_models": True,
            "live_trading": True,
            "zerodha": True,
            "paper_trading": True
        }
    }


# ============================================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ============================================================================

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Sends periodic updates about positions, P&L, and engine status.
    """
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        while True:
            # Send updates every 1 second
            # In production, this would fetch real data from engine
            update = {
                "type": "update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "positions": [],  # Will be populated with real data
                    "pnl": 0.0,
                    "engine_status": "running"
                }
            }
            
            await websocket.send_json(update)
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        active_websockets.remove(websocket)


async def broadcast_update(data: Dict[str, Any]):
    """
    Broadcast update to all connected WebSocket clients.
    
    Args:
        data: Data to broadcast
    """
    # Remove disconnected clients
    disconnected = []
    
    for ws in active_websockets:
        try:
            await ws.send_json(data)
        except:
            disconnected.append(ws)
    
    for ws in disconnected:
        active_websockets.remove(ws)


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup."""
    print("🚀 QuantX API starting...")
    print(f"📊 Version: {__version__}")
    print("📡 WebSocket available at: ws://localhost:8000/ws/live")
    print("📝 API docs available at: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    print("👋 QuantX API shutting down...")
    
    # Close all WebSocket connections
    for ws in active_websockets:
        await ws.close()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "quantx.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
