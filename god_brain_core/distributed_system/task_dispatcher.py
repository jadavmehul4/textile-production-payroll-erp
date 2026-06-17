import asyncio
from loguru import logger
from distributed_system.message_bus import MessageBus
from project_execution.task_planner import TaskPlanner

class TaskDispatcher:
    """Intelligently distributes task load across the brain node cluster."""

    def __init__(self, bus: MessageBus, node_registry):
        self.bus = bus
        self.registry = node_registry

    async def dispatch_task(self, task: dict):
        """Selects optimal node and dispatches task."""
        nodes = self.registry.get_active_nodes()
        if not nodes:
            logger.warning("DISPATCHER: No active nodes found. Using global broadcast.")
            target = "global"
        else:
            # Simple round-robin or capability matching logic
            # For Phase 7/8, we use a simple selection
            target = nodes[0]

        logger.info("DISPATCHER: Routing task {} to {}", task.get("id"), target)

        message = {
            "type": "TASK_ASSIGNMENT",
            "task": task,
            "sender": "CORE_DISPATCHER",
            "timestamp": "now"
        }

        topic = f"tasks.{target}" if target != "global" else "tasks.global"
        await self.bus.publish(topic, message)
        return True
