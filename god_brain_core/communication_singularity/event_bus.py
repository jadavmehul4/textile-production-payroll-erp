import asyncio
from loguru import logger
from typing import Callable, Dict, List

class EventBus:
    """Internal event-driven architecture for fine-grained task lifecycle management."""

    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        """Registers a listener for an event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        logger.debug("EVENT: New listener for {}", event_type)

    async def emit(self, event_type: str, data: dict):
        """Broadcasts an event to all subscribers."""
        logger.debug("EVENT: Emitting {} - {}", event_type, list(data.keys()))
        if event_type in self.listeners:
            tasks = [
                asyncio.create_task(callback(data))
                for callback in self.listeners[event_type]
            ]
            if tasks:
                await asyncio.gather(*tasks)
