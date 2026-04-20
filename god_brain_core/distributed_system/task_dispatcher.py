import asyncio
from loguru import logger
from distributed_system.message_bus import MessageBus

class TaskDispatcher:
    """Distributes tasks across active nodes."""

    def __init__(self, bus: MessageBus):
        self.bus = bus

    async def dispatch_task(self, task: dict, target_node: str = "broadcast"):
        """Sends a task to a specific node or the entire network."""
        logger.info("DISTRIBUTED: Dispatching task {} to {}", task.get("id"), target_node)

        message = {
            "type": "TASK_ASSIGNMENT",
            "task": task,
            "sender": "DISPATCHER"
        }

        topic = f"tasks.{target_node}" if target_node != "broadcast" else "tasks.global"
        await self.bus.publish(topic, message)
        return True
