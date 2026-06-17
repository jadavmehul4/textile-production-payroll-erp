from tools.base_tool import BaseTool
from loguru import logger

class LoggerTool(BaseTool):
    """A tool that logs events to the system log."""

    def __init__(self):
        super().__init__(
            name="LoggerTool",
            description="Logs messages to the system output."
        )

    async def execute(self, message: str, level: str = "INFO"):
        """Logs the provided message."""
        if level.upper() == "INFO":
            logger.info("[TOOL:Logger] {}", message)
        elif level.upper() == "SUCCESS":
            logger.success("[TOOL:Logger] {}", message)
        elif level.upper() == "WARNING":
            logger.warning("[TOOL:Logger] {}", message)
        elif level.upper() == "ERROR":
            logger.error("[TOOL:Logger] {}", message)
        else:
            logger.debug("[TOOL:Logger] {}", message)

        return {"status": "success", "logged": message}
