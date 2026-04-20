import asyncio
from loguru import logger
from distributed_system.message_bus import MessageBus
from infrastructure.task_runner import TaskRunner

class BrainNode:
    """A processing unit in the Ω GOD_BRAIN_CORE_Ω distributed network."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.bus = MessageBus()
        self.runner = TaskRunner()
        self.status = "IDLE"

    async def start(self):
        """Initializes the node and starts listening for tasks."""
        logger.info("DISTRIBUTED: Starting Brain Node: {}", self.node_id)
        await self.bus.connect()
        await self.bus.subscribe(f"tasks.{self.node_id}", self._on_task_received)
        await self.bus.subscribe("tasks.global", self._on_task_received)
        self.status = "ONLINE"

    async def _on_task_received(self, message: dict):
        """Callback for task assignment."""
        task = message.get("task")
        logger.info("NODE {}: Task received - {}", self.node_id, task.get("task"))

        self.status = "BUSY"
        # In real code, we would run the task logic
        await asyncio.sleep(1)
        self.status = "ONLINE"

        await self.bus.publish("tasks.results", {
            "node_id": self.node_id,
            "task_id": task.get("id"),
            "status": "completed"
        })
