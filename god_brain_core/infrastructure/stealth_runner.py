import asyncio
import threading
from loguru import logger

class StealthRunner:
    """Handles detached background threads for silent execution (The Ghost Protocol)."""

    def __init__(self):
        self.active_ghosts = {}

    async def execute_ghost_thread(self, task_id: str, coro):
        """Runs a task in a detached asynchronous loop in the background."""
        logger.info("Ghost Protocol: Detaching task {} for stealth execution.", task_id)

        # Start the coroutine in the background
        loop = asyncio.get_running_loop()
        future = asyncio.ensure_future(self._run_ghost(task_id, coro))
        self.active_ghosts[task_id] = future

        # Immediate audio confirmation simulation
        logger.success("Ghost Thread {} initialized. Operating silently.", task_id)
        return True

    async def _run_ghost(self, task_id: str, coro):
        try:
            result = await coro
            logger.debug("Ghost Task {} completed silently. Status: SUCCESS.", task_id)
            return result
        except Exception as e:
            logger.error("Ghost Task {} failed silently: {}", task_id, e)
        finally:
            if task_id in self.active_ghosts:
                del self.active_ghosts[task_id]

    async def list_ghost_processes(self):
        return list(self.active_ghosts.keys())
