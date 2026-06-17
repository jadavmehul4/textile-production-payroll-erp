import asyncio
from loguru import logger

class ResourceController:
    """Manages system resource limits and API quotas."""

    def __init__(self):
        self.limits = {
            "max_concurrent_tasks": 10,
            "max_memory_per_task_mb": 512,
            "api_rate_limit_per_min": 60
        }
        self.current_usage = {"tasks": 0, "api_calls": 0}

    async def check_availability(self):
        """Checks if resources are available for a new task."""
        if self.current_usage["tasks"] >= self.limits["max_concurrent_tasks"]:
            return False, "Max task concurrency reached"
        return True, "Available"

    async def track_usage(self, resource_type: str, amount: int = 1):
        """Updates resource usage counters."""
        if resource_type in self.current_usage:
            self.current_usage[resource_type] += amount
            logger.debug("Resource usage updated: {} = {}", resource_type, self.current_usage[resource_type])
