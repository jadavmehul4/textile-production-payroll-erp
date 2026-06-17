import asyncio
from loguru import logger
from distributed_system.message_bus import MessageBus
from infrastructure.task_runner import TaskRunner
from tools.tool_registry import ToolRegistry
from omniversal_memory.knowledge_brain import KnowledgeBrain

class BrainNode:
    """A high-performance processing unit in the Ω GOD_BRAIN_CORE_Ω distributed network."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.bus = MessageBus()
        self.registry = ToolRegistry()
        self.knowledge = KnowledgeBrain()
        from project_execution.execution_engine import ExecutionEngine
        self.engine = ExecutionEngine(self.registry, self.knowledge)
        self.status = "IDLE"

    async def start(self):
        """Initializes the node and joins the distributed collective."""
        logger.info("DISTRIBUTED: Activating Brain Node: {}", self.node_id)

        # Load local capabilities
        self.registry.discover_tools()

        await self.bus.connect()
        # Direct task queue
        await self.bus.subscribe(f"tasks.{self.node_id}", self._handle_direct_assignment)
        # Global broadcast queue
        await self.bus.subscribe("tasks.global", self._handle_broadcast_assignment)

        self.status = "ONLINE"
        logger.success("NODE {}: Fully operational and synchronized.", self.node_id)

    async def _handle_direct_assignment(self, message: dict):
        await self._process_assigned_task(message.get("task"))

    async def _handle_broadcast_assignment(self, message: dict):
        # In a real system, nodes would compete or use a consensus leader to claim
        task = message.get("task")
        logger.info("NODE {}: Considering broadcast task - {}", self.node_id, task.get("task"))
        await self._process_assigned_task(task)

    async def _process_assigned_task(self, task: dict):
        if not task: return

        self.status = "BUSY"
        logger.info("NODE {}: Processing task '{}'", self.node_id, task.get("task"))

        try:
            result = await self.engine.execute_task(task)

            await self.bus.publish("tasks.results", {
                "node_id": self.node_id,
                "task_id": task.get("id"),
                "result": result,
                "status": "COMPLETED" if result["status"] == "success" else "FAILED"
            })
        except Exception as e:
            logger.error("NODE {}: Task execution crashed: {}", self.node_id, e)
        finally:
            self.status = "ONLINE"
