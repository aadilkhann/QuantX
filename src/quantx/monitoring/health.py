"""
Health monitoring and metrics for QuantX.

Provides health checks, Prometheus metrics, and system monitoring.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Health check result."""
    status: HealthStatus
    timestamp: datetime
    details: Dict[str, Any]
    message: Optional[str] = None


class HealthMonitor:
    """
    System health monitoring.
    
    Tracks component health and provides unified health status.
    """
    
    def __init__(self):
        self.components: Dict[str, HealthCheck] = {}
        self.last_check: Optional[datetime] = None
    
    def check_component(
        self,
        name: str,
        check_func: callable
    ) -> HealthCheck:
        """
        Check a component's health.
        
        Args:
            name: Component name
            check_func: Function that returns (status, details) tuple
            
        Returns:
            Health check result
        """
        try:
            status, details = check_func()
            health = HealthCheck(
                status=status,
                timestamp=datetime.now(),
                details=details
            )
        except Exception as e:
            health = HealthCheck(
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(),
                details={"error": str(e)},
                message=f"Health check failed: {e}"
            )
        
        self.components[name] = health
        return health
    
    def get_overall_health(self) -> HealthCheck:
        """
        Get overall system health.
        
        Returns:
            Aggregated health status
        """
        self.last_check = datetime.now()
        
        if not self.components:
            return HealthCheck(
                status=HealthStatus.HEALTHY,
                timestamp=self.last_check,
                details={"message": "No components registered"}
            )
        
        # Determine overall status
        statuses = [check.status for check in self.components.values()]
        
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        elif any(s == Health Status.DEGRADED for s in statuses):
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY
        
        return HealthCheck(
            status=overall,
            timestamp=self.last_check,
            details={
                "components": {
                    name: {
                        "status": check.status.value,
                        "timestamp": check.timestamp.isoformat(),
                        "details": check.details
                    }
                    for name, check in self.components.items()
                }
            }
        )
    
    def get_health_dict(self) -> Dict[str, Any]:
        """
        Get health as dictionary (for API response).
        
        Returns:
            Health status dictionary
        """
        overall = self.get_overall_health()
        
        return {
            "status": overall.status.value,
            "timestamp": overall.timestamp.isoformat(),
            "components": overall.details.get("components", {})
        }
    
    def check_engine_health(self, engine) -> tuple:
        """Check live execution engine health."""
        from quantx.execution.live_engine import EngineState
        
        if engine.state == EngineState.RUNNING:
            return HealthStatus.HEALTHY, {
                "state": engine.state.value,
                "uptime": engine.get_uptime()
            }
        elif engine.state in [EngineState.STARTING, EngineState.STOPPING]:
            return HealthStatus.DEGRADED, {
                "state": engine.state.value
            }
        else:
            return HealthStatus.UNHEALTHY, {
                "state": engine.state.value
            }
    
    def check_broker_health(self, broker) -> tuple:
        """Check broker connection health."""
        if broker.is_connected():
            return HealthStatus.HEALTHY, {
                "connected": True,
                "broker": broker.name
            }
        else:
            return HealthStatus.UNHEALTHY, {
                "connected": False,
                "broker": broker.name
            }
    
    def check_event_bus_health(self, event_bus) -> tuple:
        """Check event bus health."""
        if hasattr(event_bus, '_running') and event_bus._running:
            return HealthStatus.HEALTHY, {
                "running": True
            }
        else:
            return HealthStatus.UNHEALTHY, {
                "running": False
            }


class MetricsCollector:
    """
    Metrics collection for Prometheus.
    
    Tracks key trading metrics.
    """
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "orders_total": 0,
            "orders_filled": 0,
            "orders_rejected": 0,
            "positions_count": 0,
            "pnl_total": 0.0,
            "latency_ms": [],
        }
    
    def increment(self, metric: str, value: float = 1.0):
        """Increment a counter metric."""
        if metric in self.metrics:
            self.metrics[metric] += value
    
    def set_gauge(self, metric: str, value: float):
        """Set a gauge metric."""
        self.metrics[metric] = value
    
    def observe_latency(self, latency_ms: float):
        """Record latency observation."""
        self.metrics["latency_ms"].append(latency_ms)
        
        # Keep only last 1000 observations
        if len(self.metrics["latency_ms"]) > 1000:
            self.metrics["latency_ms"] = self.metrics["latency_ms"][-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        metrics = self.metrics.copy()
        
        # Calculate latency percentiles
        if self.metrics["latency_ms"]:
            latencies = sorted(self.metrics["latency_ms"])
            n = len(latencies)
            metrics["latency_p50"] = latencies[int(n * 0.5)]
            metrics["latency_p95"] = latencies[int(n * 0.95)]
            metrics["latency_p99"] = latencies[int(n * 0.99)]
        
        return metrics
