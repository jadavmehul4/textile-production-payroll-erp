import asyncio
from loguru import logger
from infrastructure.execution_sandbox import ExecutionSandbox
from infrastructure.container_manager import ContainerManager
from infrastructure.resource_controller import ResourceController

class TaskRunner:
    """Orchestrates high-level infrastructure for task execution."""

    def __init__(self):
        self.sandbox = ExecutionSandbox()
        self.containers = ContainerManager()
        self.resources = ResourceController()

    async def run_code_task(self, task_id: str, code: str, arguments: dict):
        """Full infrastructure pipeline for code-based tasks."""
        logger.info("INFRA: Starting task runner pipeline for {}", task_id)

        # 1. Resource check
        available, msg = await self.resources.check_availability()
        if not available:
            return {"status": "resource_error", "message": msg}

        # 2. Provision environment
        await self.containers.provision_environment(task_id)
        await self.resources.track_usage("tasks", 1)

        try:
            # 3. Execution
            result = await self.sandbox.run_safely(code, arguments)
            return result
        finally:
            # 4. Cleanup
            await self.containers.cleanup_environment(task_id)
            await self.resources.track_usage("tasks", -1)
