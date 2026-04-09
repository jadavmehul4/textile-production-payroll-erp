import asyncio
from typing import Callable, Dict, List, Any

class EventBus:
    """
    A simple asynchronous event bus for handling internal system events.
    """
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def register(self, event: str, handler: Callable):
        """
        Register a handler for a specific event.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    async def emit(self, event: str, data: Any = None):
        """
        Emit an event and trigger all registered handlers asynchronously.
        """
        if event in self._handlers:
            tasks = [handler(data) for handler in self._handlers[event]]
            if tasks:
                await asyncio.gather(*tasks)

# Global event bus instance
event_bus = EventBus()
