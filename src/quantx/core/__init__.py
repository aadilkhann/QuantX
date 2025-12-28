"""Core module initialization"""

__version__ = "1.0.0"

from quantx.core.config import Config, get_config
from quantx.core.events import Event, EventBus, EventType

__all__ = ["Config", "get_config", "Event", "EventBus", "EventType", "__version__"]
