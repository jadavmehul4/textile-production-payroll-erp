import os
import datetime
from loguru import logger

class WorldState:
    """Provides system and environment context for world awareness."""

    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.system_name = "Ω GOD_BRAIN_CORE_Ω"

    async def get_state(self):
        """Returns the current state of the system and its environment."""
        now = datetime.datetime.now()
        uptime = now - self.start_time

        state = {
            "system_time": now.isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "system_name": self.system_name,
            "environment": "Sovereign Cognitive Operating System (SCOS)",
            "cwd": os.getcwd(),
            "workspace": "/app/god_brain_core/workspace/",
            "status": "Operational"
        }

        logger.debug("Captured world state at {}", state["system_time"])
        return state
