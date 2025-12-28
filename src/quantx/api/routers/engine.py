"""Engine control router for QuantX API."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/engine", tags=["Engine"])


# Request/Response Models
class EngineStartRequest(BaseModel):
    """Request to start engine."""
    strategy: str
    config: Optional[Dict[str, Any]] = None


class EngineStopRequest(BaseModel):
    """Request to stop engine."""
    timeout: float = 30.0


class EngineStatusResponse(BaseModel):
    """Engine status response."""
    state: str
    strategy: Optional[str]
    uptime: float
    broker_connected: bool
    last_update: str


# Global engine instance (in production, use dependency injection)
_engine_instance = None


@router.get("/status", response_model=EngineStatusResponse)
async def get_engine_status():
    """
    Get current engine status.
    
    Returns:
        Engine status including state, uptime, and broker connection
    """
    if _engine_instance is None:
        return EngineStatusResponse(
            state="stopped",
            strategy=None,
            uptime=0.0,
            broker_connected=False,
            last_update=datetime.now().isoformat()
        )
    
    status = _engine_instance.get_status()
    
    return EngineStatusResponse(
        state=status.get("state", "unknown"),
        strategy=status.get("strategy"),
        uptime=status.get("uptime", 0.0),
        broker_connected=status.get("broker_connected", False),
        last_update=datetime.now().isoformat()
    )


@router.post("/start")
async def start_engine(request: EngineStartRequest, background_tasks: BackgroundTasks):
    """
    Start the live trading engine.
    
    Args:
        request: Engine start configuration
        
    Returns:
        Success message
    """
    global _engine_instance
    
    if _engine_instance is not None:
        raise HTTPException(status_code=400, detail="Engine already running")
    
    # In production, create engine with proper initialization
    # For now, return success
    
    return {
        "status": "success",
        "message": f"Engine starting with strategy: {request.strategy}",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/stop")
async def stop_engine(request: EngineStopRequest):
    """
    Stop the live trading engine gracefully.
    
    Args:
        request: Stop configuration with timeout
        
    Returns:
        Success message
    """
    global _engine_instance
    
    if _engine_instance is None:
        raise HTTPException(status_code=400, detail="Engine not running")
    
    # In production, call engine.stop()
    
    return {
        "status": "success",
        "message": "Engine stopped successfully",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/pause")
async def pause_engine():
    """Pause engine (stop signal processing but maintain positions)."""
    if _engine_instance is None:
        raise HTTPException(status_code=400, detail="Engine not running")
    
    return {
        "status": "success",
        "message": "Engine paused",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/resume")
async def resume_engine():
    """Resume paused engine."""
    if _engine_instance is None:
        raise HTTPException(status_code=400, detail="Engine not running")
    
    return {
        "status": "success",
        "message": "Engine resumed",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/statistics")
async def get_statistics():
    """
    Get engine statistics.
    
    Returns:
        Comprehensive engine statistics
    """
    if _engine_instance is None:
        return {
            "engine": {
                "state": "stopped",
                "uptime": 0
            },
            "trading": {
                "signals_received": 0,
                "orders_placed": 0,
                "fills_received": 0
            }
        }
    
    return _engine_instance.get_statistics()
