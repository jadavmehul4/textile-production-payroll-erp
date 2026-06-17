from abc import ABC, abstractmethod
from loguru import logger

class BaseTool(ABC):
    """Base class for all Ω GOD_BRAIN_CORE_Ω tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs):
        """Executes the tool with given arguments."""
        pass
